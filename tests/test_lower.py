import pytest
from tests import tests, data
from vbancmd import kinds
import re


class TestPublicPacketLower:
    __test__ = True

    """Tests for a valid rt data packet"""

    def test_it_gets_an_rt_data_packet(self):
        assert tests.public_packet.voicemeetertype in (kind.id for kind in kinds.all)


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
    def test_it_gets_an_rt_data_packet(self, kls, index, param, value):
        tests.set_rt(f"{kls}[{index}]", param, value)
        target = getattr(tests, kls)[index]
        assert getattr(target, param) == bool(value)
