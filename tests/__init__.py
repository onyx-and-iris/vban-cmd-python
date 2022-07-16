import random
import sys
from dataclasses import dataclass

import vban_cmd
from vban_cmd.kinds import KindId, kinds_all
from vban_cmd.kinds import request_kind_map as kindmap

# let's keep things random
kind_id = random.choice(tuple(kind_id.name.lower() for kind_id in KindId))

opts = {
    "ip": "ws.local",
    "streamname": "workstation",
    "port": 6990,
    "bps": 0,
    "sync": True,
}

vbans = {kind.name: vban_cmd.api(kind.name, **opts) for kind in kinds_all}
tests = vbans[kind_id]
kind = kindmap(kind_id)


@dataclass
class Data:
    """bounds data to map tests to a kind"""

    name: str = kind.name
    phys_in: int = kind.ins[0] - 1
    virt_in: int = kind.ins[0] + kind.ins[1] - 1
    phys_out: int = kind.outs[0] - 1
    virt_out: int = kind.outs[0] + kind.outs[1] - 1
    vban_in: int = kind.vban[0] - 1
    vban_out: int = kind.vban[1] - 1
    button_lower: int = 0
    button_upper: int = 79


data = Data()


def setup_module():
    print(f"\nRunning tests for kind [{data.name}]\n", file=sys.stdout)
    tests.login()
    tests.command.reset()


def teardown_module():
    tests.logout()
