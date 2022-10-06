import logging

import obsws_python as obs
import vban_cmd


def on_start():
    vban.strip[0].mute = True
    vban.strip[1].B1 = True
    vban.strip[2].B2 = True


def on_brb():
    vban.strip[7].fadeto(0, 500)
    vban.bus[0].mute = True


def on_end():
    vban.apply(
        {
            "strip-0": {"mute": True},
            "strip-1": {"mute": True, "B1": False},
            "strip-2": {"mute": True, "B1": False},
        }
    )


def on_live():
    vban.strip[0].mute = False
    vban.strip[7].fadeto(-6, 500)
    vban.strip[7].A3 = True


def on_current_program_scene_changed(data):
    scene = data.scene_name
    print(f"Switched to scene {scene}")

    match scene:
        case "START":
            on_start()
        case "BRB":
            on_brb()
        case "END":
            on_end()
        case "LIVE":
            on_live()
        case _:
            pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    kind_id = "potato"
    opts = {
        "ip": "gamepc.local",
        "streamname": "Command1",
        "port": 6980,
        "subs": {"pdirty": False},
        "sync": True,
    }

    with vban_cmd.api(kind_id, **opts) as vban:
        cl = obs.EventClient()
        cl.callback.register(on_current_program_scene_changed)

        while cmd := input("Press <Enter> to exit\n"):
            if not cmd:
                break
