import pytest

from tests import data, tests


class TestRemoteFactories:
    __test__ = True

    @pytest.mark.skipif(
        data.name != "basic",
        reason="Skip test if kind is not basic",
    )
    def test_it_tests_remote_attrs_for_basic(self):
        assert hasattr(tests, "strip")
        assert hasattr(tests, "bus")
        assert hasattr(tests, "command")

        assert len(tests.strip) == 3
        assert len(tests.bus) == 2

    @pytest.mark.skipif(
        data.name != "banana",
        reason="Skip test if kind is not basic",
    )
    def test_it_tests_remote_attrs_for_banana(self):
        assert hasattr(tests, "strip")
        assert hasattr(tests, "bus")
        assert hasattr(tests, "command")

        assert len(tests.strip) == 5
        assert len(tests.bus) == 5

    @pytest.mark.skipif(
        data.name != "potato",
        reason="Skip test if kind is not basic",
    )
    def test_it_tests_remote_attrs_for_potato(self):
        assert hasattr(tests, "strip")
        assert hasattr(tests, "bus")
        assert hasattr(tests, "command")

        assert len(tests.strip) == 8
        assert len(tests.bus) == 8
