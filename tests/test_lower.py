import pytest

from tests import data, vban
from vban_cmd import kinds


class TestPublicPacketLower:
    __test__ = True

    """Tests for a valid rt data packet"""

    def test_it_gets_an_rt_data_packet(self):
        assert vban.public_packet.voicemeetertype in (
            kind.name for kind in kinds.kinds_all
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
        vban._set_rt(f"{kls}[{index}].{param}", value)
        target = getattr(vban, kls)[index]
        assert getattr(target, param) == bool(value)
