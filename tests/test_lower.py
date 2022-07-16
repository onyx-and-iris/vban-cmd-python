import time

import pytest
from vban_cmd import kinds

from tests import data, tests


class TestPublicPacketLower:
    __test__ = True

    """Tests for a valid rt data packet"""

    def test_it_gets_an_rt_data_packet(self):
        assert tests.public_packet.voicemeetertype in (
            kind.name for kind in kinds.kinds_all
        )


@pytest.mark.skipif(
    "not config.getoption('--run-slow')",
    reason="Only run when --run-slow is given",
)
@pytest.mark.parametrize("value", [0, 1])
class TestSetRT:
    __test__ = True

    """Tests set_rt"""

    @pytest.mark.parametrize(
        "kls,index,param",
        [
            ("strip", data.phys_in, "mute"),
            ("bus", data.virt_out, "mono"),
        ],
    )
    def test_it_sends_a_text_request(self, kls, index, param, value):
        tests._set_rt(f"{kls}[{index}]", param, value)
        time.sleep(0.02)
        target = getattr(tests, kls)[index]
        assert getattr(target, param) == bool(value)
