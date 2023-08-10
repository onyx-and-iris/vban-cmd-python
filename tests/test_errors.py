import pytest

import vban_cmd
from tests import data, vban


class TestErrors:
    __test__ = True

    def test_it_tests_an_unknown_kind(self):
        with pytest.raises(
            vban_cmd.error.VBANCMDError,
            match=f"Unknown Voicemeeter kind 'unknown_kind'",
        ):
            vban_cmd.api("unknown_kind")

    def test_it_tests_an_unknown_config_name(self):
        EXPECTED_MSG = (
            f"No config with name 'unknown' is loaded into memory",
            f"Known configs: {list(vban.configs.keys())}",
        )
        with pytest.raises(vban_cmd.error.VBANCMDError) as exc_info:
            vban.apply_config("unknown")

        e = exc_info.value
        assert e.message == "\n".join(EXPECTED_MSG)

    def test_it_tests_an_invalid_config_key(self):
        CONFIG = {
            "strip-0": {"A1": True, "B1": True, "gain": -6.0},
            "bus-0": {"mute": True, "eq": {"on": True}},
            "unknown-0": {"state": True},
            "vban-out-1": {"name": "streamname"},
        }
        with pytest.raises(ValueError, match="invalid config key 'unknown-0'"):
            vban.apply(CONFIG)
