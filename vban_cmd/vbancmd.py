import abc
import logging
import socket
import threading
import time
from pathlib import Path
from queue import Queue
from typing import Mapping, Union

from .enums import NBS
from .error import VBANCMDConnectionError, VBANCMDError
from .event import Event
from .packet.headers import (
    VbanMatrixResponseHeader,
    VbanPongHeader,
    VbanRequestHeader,
)
from .packet.ping0 import VbanPing0Payload, VbanServerType
from .subject import Subject
from .util import bump_framecounter, deep_merge, pong_timeout, ratelimit
from .worker import Producer, Subscriber, Updater

logger = logging.getLogger(__name__)


class VbanCmd(abc.ABC):
    """Abstract Base Class for Voicemeeter VBAN Command Interfaces"""

    DELAY = 0.001
    # fmt: off
    BPS_OPTS = [
        0, 110, 150, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 31250,
        38400, 57600, 115200, 128000, 230400, 250000, 256000, 460800, 921600,
        1000000, 1500000, 2000000, 3000000,
    ]
    # fmt: on

    def __init__(self, **kwargs):
        self.logger = logger.getChild(self.__class__.__name__)
        self.event = Event({k: kwargs.pop(k) for k in ('pdirty', 'ldirty')})
        if not kwargs['host']:
            kwargs |= self._conn_from_toml()
        for attr, val in kwargs.items():
            setattr(self, attr, val)

        self._framecounter = 0
        self._framecounter_lock = threading.Lock()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(self.timeout)
        self.subject = self.observer = Subject()
        self.cache = {}
        self._pdirty = False
        self._ldirty = False
        self.stop_event = None
        self.producer = None
        self._last_script_request_time = 0

    @abc.abstractmethod
    def __str__(self):
        """Ensure subclasses override str magic method"""

    def _conn_from_toml(self) -> dict:
        try:
            import tomllib
        except ModuleNotFoundError:
            import tomli as tomllib  # type: ignore[import]

        def get_filepath():
            for pn in (
                Path.cwd() / 'vban.toml',
                Path.cwd() / 'configs' / 'vban.toml',
                Path.home() / '.config' / 'vban-cmd' / 'vban.toml',
                Path.home() / 'Documents' / 'Voicemeeter' / 'configs' / 'vban.toml',
            ):
                if pn.exists():
                    return pn

        if not (filepath := get_filepath()):
            raise VBANCMDError('no ip provided and no vban.toml located.')
        try:
            with open(filepath, 'rb') as f:
                return tomllib.load(f)['connection']
        except tomllib.TomlDecodeError as e:
            raise VBANCMDError(f'Error decoding {filepath}: {e}') from e

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        self.logout()

    def login(self) -> None:
        """Sends a PING packet to the VBAN server to verify connectivity and detect server type.
        If the server is detected as Matrix, RT listeners will be disabled for compatibility.
        """
        self._ping()
        self._handle_pong()

        if not self.disable_rt_listeners:
            self.event.info()

            self.stop_event = threading.Event()
            self.stop_event.clear()
            self.subscriber = Subscriber(self, self.stop_event)
            self.subscriber.start()

            queue = Queue()
            self.updater = Updater(self, queue)
            self.updater.start()
            self.producer = Producer(self, queue, self.stop_event)
            self.producer.start()

        self.logger.info(
            "Successfully logged into VBANCMD {kind} with host='{host}', port={port}, streamname='{streamname}'".format(
                **self.__dict__
            )
        )

    def logout(self) -> None:
        if not self.stopped():
            self.logger.debug('events thread shutdown started')
            self.stop_event.set()
            if self.producer is not None:
                for t in (self.producer, self.subscriber):
                    t.join()
        self.sock.close()
        self.logger.info(f'{type(self).__name__}: Successfully logged out of {self}')

    def stopped(self):
        return self.stop_event is None or self.stop_event.is_set()

    def _get_next_framecounter(self) -> int:
        """Thread-safe method to get and increment framecounter."""
        with self._framecounter_lock:
            current = self._framecounter
            self._framecounter = bump_framecounter(self._framecounter)
            return current

    def _ping(self):
        """Initiates the PING/PONG handshake with the VBAN server."""
        try:
            self.sock.sendto(
                VbanPing0Payload.create_packet(self._get_next_framecounter()),
                (socket.gethostbyname(self.host), self.port),
            )
            self.logger.debug(f'PING sent to {self.host}:{self.port}')

        except socket.gaierror as e:
            raise VBANCMDConnectionError(
                f'Unable to resolve hostname {self.host}'
            ) from e
        except Exception as e:
            raise VBANCMDConnectionError(f'PING failed: {e}') from e

    @pong_timeout
    def _handle_pong(self) -> bool:
        """Handles incoming packets during the PING/PONG handshake, looking for a valid PONG response to confirm connectivity and detect server type.

        Returns True if a valid PONG is received, False otherwise."""
        data, addr = self.sock.recvfrom(2048)

        if VbanPongHeader.is_pong_response(data):
            self.logger.debug(f'PONG received from {addr}, connectivity confirmed')

            server_type = VbanPing0Payload.detect_server_type(data)
            self._handle_server_type(server_type)

            return True
        else:
            if len(data) >= 8:
                if data[:4] == b'VBAN':
                    protocol = data[4] & 0xE0
                    nbc = data[6]
                    self.logger.debug(
                        f'Non-PONG VBAN packet: protocol=0x{protocol:02x}, nbc=0x{nbc:02x}'
                    )
                else:
                    self.logger.debug('Non-VBAN packet received')

            return False

    def _handle_server_type(self, server_type: VbanServerType) -> None:
        """Handle the detected server type by adjusting settings accordingly."""
        match server_type:
            case VbanServerType.VOICEMEETER:
                self.logger.debug(
                    'Detected Voicemeeter VBAN server - RT listeners supported'
                )
            case VbanServerType.MATRIX:
                self.logger.info(
                    'Detected Matrix VBAN server - disabling RT listeners for compatibility'
                )
                self.disable_rt_listeners = True
            case _:
                self.logger.debug(
                    f'Unknown server type ({server_type}) - using default settings'
                )

    def _send_request(self, payload: str) -> None:
        """Sends a request packet over the network and bumps the framecounter."""
        self.sock.sendto(
            VbanRequestHeader.encode_with_payload(
                name=self.streamname,
                bps_index=self.BPS_OPTS.index(self.bps),
                channel=self.channel,
                framecounter=self._get_next_framecounter(),
                payload=payload,
            ),
            (socket.gethostbyname(self.host), self.port),
        )

    def _set_rt(self, cmd: str, val: Union[str, float]):
        """Sends a string request command over a network."""
        self._send_request(f'{cmd}={val};')
        self.cache[cmd] = val

    @ratelimit
    def sendtext(self, script) -> str | None:
        """Sends a multiple parameter string over a network."""
        self._send_request(script)
        self.logger.debug(f'sendtext: {script}')

        if self.disable_rt_listeners and script.endswith(('?', '?;')):
            try:
                data, _ = self.sock.recvfrom(2048)
                return VbanMatrixResponseHeader.extract_payload(data)
            except ValueError as e:
                self.logger.warning(f'Error extracting matrix response: {e}')
            except TimeoutError as e:
                self.logger.exception(f'Timeout waiting for matrix response: {e}')
                raise VBANCMDConnectionError(
                    f'Timeout waiting for response from {self.host}:{self.port}'
                ) from e

    @property
    def type(self) -> str:
        """Returns the type of Voicemeeter installation."""
        return self.public_packets[NBS.zero].voicemeetertype

    @property
    def version(self) -> str:
        """Returns Voicemeeter's version as a string"""
        return '{0}.{1}.{2}.{3}'.format(
            *self.public_packets[NBS.zero].voicemeeterversion
        )

    @property
    def pdirty(self):
        """True iff a parameter has changed"""
        return self._pdirty

    @property
    def ldirty(self):
        """True iff a level value has changed."""
        return self._ldirty

    @property
    def public_packets(self):
        return self._public_packets

    def clear_dirty(self) -> None:
        while self.pdirty:
            time.sleep(self.DELAY)

    def apply(self, data: Mapping):
        """Set all parameters of a dict"""

        def target(key):
            match key.split('-'):
                case ['strip' | 'bus' as kls, index] if index.isnumeric():
                    target = getattr(self, kls)
                case [
                    'vban',
                    'in' | 'instream' | 'out' | 'outstream' as direction,
                    index,
                ] if index.isnumeric():
                    target = getattr(
                        self.vban, f'{direction.removesuffix("stream")}stream'
                    )
                case _:
                    ERR_MSG = f"invalid config key '{key}'"
                    self.logger.error(ERR_MSG)
                    raise ValueError(ERR_MSG)
            return target[int(index)]

        for key, di in data.items():
            target(key).apply(di)

    def apply_config(self, name):
        """applies a config from memory"""
        ERR_MSG = (
            f"No config with name '{name}' is loaded into memory",
            f'Known configs: {list(self.configs.keys())}',
        )
        try:
            config = self.configs[name]
        except KeyError as e:
            self.logger.error(('\n').join(ERR_MSG))
            raise VBANCMDError(('\n').join(ERR_MSG)) from e

        if 'extends' in config:
            extended = config['extends']
            config = {
                k: v
                for k, v in deep_merge(self.configs[extended], config)
                if k not in ('extends')
            }
            self.logger.debug(
                f"profile '{name}' extends '{extended}', profiles merged.."
            )
        self.apply(config)
        self.logger.info(f"Profile '{name}' applied!")
