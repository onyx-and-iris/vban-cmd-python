import pytest

from tests import data, vban


class TestRemoteFactories:
    __test__ = True

    @pytest.mark.skipif(
        data.name != "basic",
        reason="Skip test if kind is not basic",
    )
    def test_it_tests_remote_attrs_for_basic(self):
        assert hasattr(vban, "strip")
        assert hasattr(vban, "bus")
        assert hasattr(vban, "command")
        assert hasattr(vban, "button")
        assert hasattr(vban, "vban")

        assert len(vban.strip) == 3
        assert len(vban.bus) == 2
        assert len(vban.button) == 80
        assert len(vban.vban.instream) == 6 and len(vban.vban.outstream) == 5

    @pytest.mark.skipif(
        data.name != "banana",
        reason="Skip test if kind is not basic",
    )
    def test_it_tests_remote_attrs_for_banana(self):
        assert hasattr(vban, "strip")
        assert hasattr(vban, "bus")
        assert hasattr(vban, "command")
        assert hasattr(vban, "button")
        assert hasattr(vban, "vban")

        assert len(vban.strip) == 5
        assert len(vban.bus) == 5
        assert len(vban.button) == 80
        assert len(vban.vban.instream) == 10 and len(vban.vban.outstream) == 9

    @pytest.mark.skipif(
        data.name != "potato",
        reason="Skip test if kind is not basic",
    )
    def test_it_tests_remote_attrs_for_potato(self):
        assert hasattr(vban, "strip")
        assert hasattr(vban, "bus")
        assert hasattr(vban, "command")
        assert hasattr(vban, "button")
        assert hasattr(vban, "vban")

        assert len(vban.strip) == 8
        assert len(vban.bus) == 8
        assert len(vban.button) == 80
        assert len(vban.vban.instream) == 10 and len(vban.vban.outstream) == 9
