import random
import sys
from dataclasses import dataclass

import vban_cmd
from vban_cmd.kinds import KindId
from vban_cmd.kinds import request_kind_map as kindmap

# let's keep things random
KIND_ID = random.choice(tuple(kind_id.name.lower() for kind_id in KindId))

opts = {
    "ip": "testing.local",
    "streamname": "testing",
    "port": 6990,
    "bps": 0,
}

vban = vban_cmd.api(KIND_ID, **opts)
kind = kindmap(KIND_ID)


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
    vban.login()
    vban.command.reset()


def teardown_module():
    vban.logout()
