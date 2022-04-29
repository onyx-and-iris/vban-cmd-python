from dataclasses import dataclass
import vbancmd
from vbancmd import kinds
import random
import sys

# let's keep things random
kind_id = random.choice(tuple(kind.id for kind in kinds.all))

opts = {
    "ip": "codey.local",
    "streamname": "testing",
    "port": 6990,
    "bps": 0,
    "sync": True,
}

vbans = {kind.id: vbancmd.connect(kind_id, **opts) for kind in kinds.all}
tests = vbans[kind_id]
kind = kinds.get(kind_id)


@dataclass
class Data:
    """bounds data to map tests to a kind"""

    name: str = kind.id
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
    tests.apply_profile("blank")


def teardown_module():
    tests.logout()
