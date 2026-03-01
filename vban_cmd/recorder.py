import os
import re

from .error import VBANCMDError
from .iremote import IRemote
from .meta import action_fn


class Recorder(IRemote):
    """
    Implements the common interface

    Defines concrete implementation for recorder
    """

    @classmethod
    def make(cls, remote):
        """
        Factory function for recorder class.

        Returns a Recorder class of a kind.
        """
        Recorder_cls = type(
            f'Recorder{remote.kind}',
            (cls,),
            {
                **{
                    param: action_fn(param)
                    for param in [
                        'play',
                        'stop',
                        'pause',
                        'replay',
                        'record',
                        'ff',
                        'rew',
                    ]
                },
            },
        )
        return Recorder_cls(remote)

    def __str__(self):
        return f'{type(self).__name__}'

    @property
    def identifier(self) -> str:
        return 'recorder'

    @property
    def samplerate(self) -> int:
        return

    @samplerate.setter
    def samplerate(self, val: int):
        opts = (22050, 24000, 32000, 44100, 48000, 88200, 96000, 176400, 192000)
        if val not in opts:
            self.logger.warning(f'samplerate got: {val} but expected a value in {opts}')
        self.setter('samplerate', val)

    @property
    def bitresolution(self) -> int:
        return

    @bitresolution.setter
    def bitresolution(self, val: int):
        opts = (8, 16, 24, 32)
        if val not in opts:
            self.logger.warning(
                f'bitresolution got: {val} but expected a value in {opts}'
            )
        self.setter('bitresolution', val)

    @property
    def channel(self) -> int:
        return

    @channel.setter
    def channel(self, val: int):
        if not 1 <= val <= 8:
            self.logger.warning(f'channel got: {val} but expected a value from 1 to 8')
        self.setter('channel', val)

    @property
    def kbps(self):
        return

    @kbps.setter
    def kbps(self, val: int):
        opts = (32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320)
        if val not in opts:
            self.logger.warning(f'kbps got: {val} but expected a value in {opts}')
        self.setter('kbps', val)

    @property
    def gain(self) -> float:
        return

    @gain.setter
    def gain(self, val: float):
        self.setter('gain', val)

    def load(self, file: os.PathLike):
        try:
            self.setter('load', str(file))
        except UnicodeError:
            raise VBANCMDError('File full directory must be a raw string')

    def goto(self, time_str):
        def get_sec():
            """Get seconds from time string"""
            h, m, s = time_str.split(':')
            return int(h) * 3600 + int(m) * 60 + int(s)

        time_str = str(time_str)  # coerce the type
        if (
            re.match(
                r'^(?:[01]\d|2[0123]):(?:[012345]\d):(?:[012345]\d)$',
                time_str,
            )
            is not None
        ):
            self.setter('goto', get_sec())
        else:
            self.logger.warning(
                "goto expects a string that matches the format 'hh:mm:ss'"
            )

    def filetype(self, val: str):
        opts = {'wav': 1, 'aiff': 2, 'bwf': 3, 'mp3': 100}
        try:
            self.setter('filetype', opts[val.lower()])
        except KeyError:
            self.logger.warning(
                f'filetype got: {val} but expected a value in {list(opts.keys())}'
            )
