class Event:
    def __init__(self, subs: dict):
        self.subs = subs

    def info(self, msg):
        info = (
            f"{msg} events",
            f"Now listening for {', '.join(self.get())} events",
        )
        print("\n".join(info))

    @property
    def pdirty(self):
        return self.subs["pdirty"]

    @property
    def ldirty(self):
        return self.subs["ldirty"]

    def get(self) -> list:
        return [k for k, v in self.subs.items() if v]

    def any(self) -> bool:
        return any(self.subs.values())

    def add(self, event):
        self.subs[event] = True
        self.info(f"{event} added to")

    def remove(self, event):
        self.subs[event] = False
        self.info(f"{event} removed from")
