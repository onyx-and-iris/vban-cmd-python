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
        self.vban.bus[3].gain = -6.3
        self.vban.bus[4].eq = True
        info = (
            f"bus 3 gain has been set to {self.vban.bus[3].gain}",
            f"bus 4 eq has been set to {self.vban.bus[4].eq}",
        )
        print("\n".join(info))


def main():
    kind_id = "banana"

    with vban_cmd.api(
        kind_id, ip="gamepc.local", port=6980, streamname="Command1"
    ) as vban:
        do = ManyThings(vban)
        do.things()
        do.other_things()

        # set many parameters at once
        vban.apply(
            {
                "strip-2": {"A1": True, "B1": True, "gain": -6.0},
                "bus-2": {"mute": True},
                "vban-in-0": {"on": True},
            }
        )


if __name__ == "__main__":
    main()
