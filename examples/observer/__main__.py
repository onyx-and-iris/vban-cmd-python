import logging

import vban_cmd


class Observer:
    def __init__(self, vban):
        self.vban = vban
        # register your app as event observer
        self.vban.subject.add(self)
        # add level updates, since they are disabled by default.
        self.vban.event.add("ldirty")

    # define an 'on_update' callback function to receive event updates
    def on_update(self, subject):
        if subject == "pdirty":
            print("pdirty!")
        elif subject == "ldirty":
            info = (
                f"[{self.vban.bus[0]} {self.vban.bus[0].levels.isdirty}]",
                f"[{self.vban.bus[1]} {self.vban.bus[1].levels.isdirty}]",
                f"[{self.vban.bus[2]} {self.vban.bus[2].levels.isdirty}]",
                f"[{self.vban.bus[3]} {self.vban.bus[3].levels.isdirty}]",
                f"[{self.vban.bus[4]} {self.vban.bus[4].levels.isdirty}]",
                f"[{self.vban.bus[5]} {self.vban.bus[5].levels.isdirty}]",
                f"[{self.vban.bus[6]} {self.vban.bus[6].levels.isdirty}]",
                f"[{self.vban.bus[7]} {self.vban.bus[7].levels.isdirty}]",
            )
            print(" ".join(info))


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
