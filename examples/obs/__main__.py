import threading
from logging import config

import obsws_python as obsws

import vban_cmd

config.dictConfig(
    {
        'version': 1,
        'formatters': {
            'standard': {
                'format': '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s'
            }
        },
        'handlers': {
            'stream': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
            }
        },
        'loggers': {
            'vban_cmd.iremote': {
                'handlers': ['stream'],
                'level': 'DEBUG',
                'propagate': False,
            }
        },
        'root': {'handlers': ['stream'], 'level': 'WARNING'},
    }
)


class Observer:
    def __init__(self, vban, stop_event):
        self._vban = vban
        self._stop_event = stop_event
        self._client = obsws.EventClient()
        self._client.callback.register(
            (
                self.on_current_program_scene_changed,
                self.on_exit_started,
            )
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._client.disconnect()

    def on_start(self):
        self._vban.strip[0].mute = True
        self._vban.strip[1].B1 = True
        self._vban.strip[2].B2 = True

    def on_brb(self):
        self._vban.strip[7].fadeto(0, 500)
        self._vban.bus[0].mute = True

    def on_end(self):
        self._vban.apply(
            {
                'strip-0': {'mute': True},
                'strip-1': {'mute': True, 'B1': False},
                'strip-2': {'mute': True, 'B1': False},
            }
        )

    def on_live(self):
        self._vban.strip[0].mute = False
        self._vban.strip[7].fadeto(-6, 500)
        self._vban.strip[7].A3 = True

    def on_current_program_scene_changed(self, data):
        scene = data.scene_name
        print(f'Switched to scene {scene}')
        match scene:
            case 'START':
                self.on_start()
            case 'BRB':
                self.on_brb()
            case 'END':
                self.on_end()
            case 'LIVE':
                self.on_live()

    def on_exit_started(self, _):
        self._stop_event.set()


def main():
    KIND_ID = 'potato'

    with vban_cmd.api(KIND_ID) as vban:
        stop_event = threading.Event()

        with Observer(vban, stop_event):
            stop_event.wait()


if __name__ == '__main__':
    main()
