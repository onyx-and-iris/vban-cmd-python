import vban_cmd


class Observer:
    def __init__(self, vban):
        self.vban = vban

    def on_update(self, subject):
        if subject == "pdirty":
            print("pdirty!")
        if subject == "ldirty":
            info = (
                f"[{self.vban.bus[0]} {self.vban.bus[0].levels.is_updated}]",
                f"[{self.vban.bus[1]} {self.vban.bus[1].levels.is_updated}]",
                f"[{self.vban.bus[2]} {self.vban.bus[2].levels.is_updated}]",
                f"[{self.vban.bus[3]} {self.vban.bus[3].levels.is_updated}]",
                f"[{self.vban.bus[4]} {self.vban.bus[4].levels.is_updated}]",
                f"[{self.vban.bus[5]} {self.vban.bus[5].levels.is_updated}]",
                f"[{self.vban.bus[6]} {self.vban.bus[6].levels.is_updated}]",
                f"[{self.vban.bus[7]} {self.vban.bus[7].levels.is_updated}]",
            )
            print(" ".join(info))


def main():
    with vban_cmd.api(kind_id, **opts) as vban:
        obs = Observer(vban)
        vban.subject.add(obs)

        while cmd := input("Press <Enter> to exit\n"):
            if not cmd:
                break


if __name__ == "__main__":
    kind_id = "potato"
    opts = {
        "ip": "<ip address>",
        "streamname": "Command1",
        "port": 6980,
    }

    main()
