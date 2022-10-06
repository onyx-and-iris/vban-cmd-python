import logging

import vban_cmd


class Observer:
    def __init__(self, vban):
        self.vban = vban
        # register your app as event observer
        self.vban.subject.add(self)
        # enable level updates, since they are disabled by default.
        self.vban.event.ldirty = True

    # define an 'on_update' callback function to receive event updates
    def on_update(self, subject):
        if subject == "pdirty":
            print("pdirty!")
        elif subject == "ldirty":
            for bus in self.vban.bus:
                if bus.levels.isdirty:
                    print(bus, bus.levels.all)


def main():
    with vban_cmd.api(kind_id, **opts) as vban:
        Observer(vban)

        while cmd := input("Press <Enter> to exit\n"):
            if not cmd:
                break


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    kind_id = "potato"
    opts = {
        "ip": "<ip address>",
        "streamname": "Command1",
        "port": 6980,
    }

    main()
