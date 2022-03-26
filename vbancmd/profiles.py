import toml
from . import kinds
from .util import project_path
from pathlib import Path

profiles = {}


def _make_blank_profile(kind):
    phys_in, virt_in = kind.ins
    phys_out, virt_out = kind.outs
    all_input_strip_config = {
        "gain": 0.0,
        "solo": False,
        "mute": False,
        "mono": False,
        **{f"A{i}": False for i in range(1, phys_out + 1)},
        **{f"B{i}": False for i in range(1, virt_out + 1)},
    }
    phys_input_strip_config = {
        "comp": 0.0,
        "gate": 0.0,
    }
    output_bus_config = {
        "gain": 0.0,
        "eq": False,
        "mute": False,
        "mono": False,
    }
    all_ = {f"strip-{i}": all_input_strip_config for i in range(phys_in + virt_in)}
    phys = {f"strip-{i}": phys_input_strip_config for i in range(phys_in)}
    abc = all_
    for i in phys.keys():
        abc[i] = all_[i] | phys[i]
    return {
        **abc,
        **{f"bus-{i}": output_bus_config for i in range(phys_out + virt_out)},
    }


def _make_base_profile(kind):
    phys_in, virt_in = kind.ins
    blank = _make_blank_profile(kind)
    overrides = {
        **{f"strip-{i}": dict(B1=True) for i in range(phys_in)},
        **{f"strip-{i}": dict(A1=True) for i in range(phys_in, phys_in + virt_in)},
    }
    base = blank
    for i in overrides.keys():
        base[i] = blank[i] | overrides[i]
    return base


for kind in kinds.all:
    profiles[kind.id] = {
        "blank": _make_blank_profile(kind),
        "base": _make_base_profile(kind),
    }

# Load profiles from config files in profiles/<kind_id>/<profile>.toml
for kind in kinds.all:
    profiles_paths = [
        Path(project_path()) / "profiles" / kind.id,
        Path.cwd() / "profiles" / kind.id,
        Path.home() / "Documents/Voicemeeter" / "profiles" / kind.id,
    ]
    for path in profiles_paths:
        if path.is_dir():
            filenames = list(path.glob("*.toml"))
            configs = {}
            for filename in filenames:
                name = filename.with_suffix("").stem
                try:
                    configs[name] = toml.load(filename)
                except toml.TomlDecodeError:
                    print(f"Invalid TOML profile: {kind.id}/{filename.stem}")

            for name, cfg in configs.items():
                print(f"Loaded profile {kind.id}/{name}")
                profiles[kind.id][name] = cfg
