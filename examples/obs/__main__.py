import logging

import obsws_python as obs
import vban_cmd

logging.basicConfig(level=logging.INFO)


class Observer:
    def __init__(self, vban):
        self.vban = vban
        self.client = obs.EventClient()
        self.client.callback.register(self.on_current_program_scene_changed)

    def on_start(self):
        self.vban.strip[0].mute = True
        self.vban.strip[1].B1 = True
        self.vban.strip[2].B2 = True

    def on_brb(self):
        self.vban.strip[7].fadeto(0, 500)
        self.vban.bus[0].mute = True

    def on_end(self):
        self.vban.apply(
            {
                "strip-0": {"mute": True},
                "strip-1": {"mute": True, "B1": False},
                "strip-2": {"mute": True, "B1": False},
            }
        )

    def on_live(self):
        self.vban.strip[0].mute = False
        self.vban.strip[7].fadeto(-6, 500)
        self.vban.strip[7].A3 = True

    def on_current_program_scene_changed(self, data):
        def fget(scene):
            run = {
                "START": self.on_start,
                "BRB": self.on_brb,
                "END": self.on_end,
                "LIVE": self.on_live,
            }
            return run.get(scene)

        scene = data.scene_name
        print(f"Switched to scene {scene}")
        if fn := fget(scene):
            fn()


def main():
    with vban_cmd.api("potato", sync=True) as vban:
        obs = Observer(vban)
        while cmd := input("<Enter> to exit\n"):
            if not cmd:
                break


if __name__ == "__main__":
    main()
