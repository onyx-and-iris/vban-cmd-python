import logging
import os

import vban_cmd

logging.basicConfig(level=logging.INFO)


class App:
    def __init__(self, vban):
        self.vban = vban
        # register your app as event observer
        self.vban.observer.add(self)

    # define an 'on_update' callback function to receive event updates
    def on_update(self, event):
        if event == 'pdirty':
            print('pdirty!')
        elif event == 'ldirty':
            for bus in self.vban.bus:
                if bus.levels.isdirty:
                    print(bus, bus.levels.all)


def main():
    KIND_ID = 'banana'
    conn = {
        'host': os.environ.get('VBANCMD_HOST', 'localhost'),
        'port': int(os.environ.get('VBANCMD_PORT', 6980)),
        'streamname': os.environ.get('VBANCMD_STREAMNAME', 'Command1'),
    }

    with vban_cmd.api(KIND_ID, pdirty=True, ldirty=True, **conn) as vban:
        App(vban)

        while _ := input('Press <Enter> to exit\n'):
            pass


if __name__ == '__main__':
    main()
