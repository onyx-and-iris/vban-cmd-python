import time

import pytest

from tests import data, vban


class TestSetAndGetBoolHigher:
    __test__ = True

    """example config tests"""

    @classmethod
    def setup_class(cls):
        vban.apply_config("example")
        time.sleep(0.1)

    @pytest.mark.skipif(
        "not config.getoption('--run-slow')",
        reason="Only run when --run-slow is given",
    )
    def test_it_tests_config_string(self):
        assert "PhysStrip" in vban.strip[data.phys_in].label
        assert "VirtStrip" in vban.strip[data.virt_in].label

    @pytest.mark.skipif(
        "not config.getoption('--run-slow')",
        reason="Only run when --run-slow is given",
    )
    def test_it_tests_config_bool(self):
        assert vban.strip[0].A1 == True

    @pytest.mark.skipif(
        "not config.getoption('--run-slow')",
        reason="Only run when --run-slow is given",
    )
    def test_it_tests_config_busmode(self):
        assert vban.bus[data.phys_out].mode.get() == "composite"
