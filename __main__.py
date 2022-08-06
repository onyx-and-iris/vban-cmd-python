import vban_cmd


class ManyThings:
    def __init__(self, vban):
        self.vban = vban

    def things(self):
        self.vban.strip[0].label = "podmic"
        self.vban.strip[0].mute = True
        print(
            f"strip 0 ({self.vban.strip[0].label}) mute has been set to {self.vban.strip[0].mute}"
        )

    def other_things(self):
        info = (
            f"bus 3 gain has been set to {self.vban.bus[3].gain}",
            f"bus 4 eq has been set to {self.vban.bus[4].eq}",
        )
        self.vban.bus[3].gain = -6.3
        self.vban.bus[4].eq = True
        print("\n".join(info))


def main():
    with vban_cmd.api(kind_id, **opts) as vban:
        do = ManyThings(vban)
        do.things()
        do.other_things()

        # set many parameters at once
        vban.apply(
            {
                "strip-2": {"A1": True, "B1": True, "gain": -6.0},
                "bus-2": {"mute": True},
                "button-0": {"state": True},
                "vban-in-0": {"on": True},
                "vban-out-1": {"name": "streamname"},
            }
        )


if __name__ == "__main__":
    kind_id = "banana"
    opts = {
        "ip": "<ip address>",
        "streamname": "Command1",
        "port": 6980,
    }

    main()
