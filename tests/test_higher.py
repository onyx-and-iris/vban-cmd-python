import pytest

from tests import data, tests


@pytest.mark.parametrize("value", [False, True])
class TestSetAndGetBoolHigher:
    __test__ = True

    """strip tests, physical and virtual"""

    @pytest.mark.parametrize(
        "index,param",
        [
            (data.phys_in, "mute"),
            (data.virt_in, "solo"),
        ],
    )
    def test_it_sets_and_gets_strip_bool_params(self, index, param, value):
        setattr(tests.strip[index], param, value)
        assert getattr(tests.strip[index], param) == value

    @pytest.mark.skipif(
        data.name == "banana",
        reason="Only test if logged into Basic or Potato version",
    )
    @pytest.mark.parametrize(
        "index,param",
        [
            (data.phys_in, "mc"),
        ],
    )
    def test_it_sets_and_gets_strip_bool_params_mc(self, index, param, value):
        setattr(tests.strip[index], param, value)
        assert getattr(tests.strip[index], param) == value

    """ bus tests, physical and virtual """

    @pytest.mark.parametrize(
        "index,param",
        [
            (data.phys_out, "eq"),
            (data.phys_out, "mute"),
            (data.virt_out, "eq_ab"),
            (data.virt_out, "sel"),
        ],
    )
    def test_it_sets_and_gets_bus_bool_params(self, index, param, value):
        setattr(tests.bus[index], param, value)
        assert getattr(tests.bus[index], param) == value

    """  bus modes tests, physical and virtual """

    @pytest.mark.parametrize(
        "index,param",
        [
            (data.phys_out, "normal"),
            (data.phys_out, "amix"),
            (data.phys_out, "rearonly"),
            (data.virt_out, "normal"),
            (data.virt_out, "upmix41"),
            (data.virt_out, "composite"),
        ],
    )
    def test_it_sets_and_gets_bus_bool_params(self, index, param, value):
        # here it only makes sense to set/get bus modes as True
        if not value:
            value = True
        setattr(tests.bus[index].mode, param, value)
        assert getattr(tests.bus[index].mode, param) == value

    """ command tests """

    @pytest.mark.parametrize(
        "param",
        [("lock")],
    )
    def test_it_sets_command_bool_params(self, param, value):
        setattr(tests.command, param, value)


class TestSetAndGetIntHigher:
    # note, currently no int parameters supported by rt packet service
    # ie they can be set but not get
    __test__ = False

    """strip tests, physical and virtual"""

    @pytest.mark.parametrize(
        "index,param,value",
        [
            (data.virt_in, "k", 0),
            (data.virt_in, "k", 4),
        ],
    )
    def test_it_sets_and_gets_strip_bool_params(self, index, param, value):
        setattr(tests.strip[index], param, value)
        assert getattr(tests.strip[index], param) == value


class TestSetAndGetFloatHigher:
    __test__ = True

    """strip tests, physical and virtual"""

    @pytest.mark.parametrize(
        "index,param,value",
        [
            (data.phys_in, "gain", -3.6),
            (data.phys_in, "gain", 3.6),
            (data.virt_in, "gain", -5.8),
            (data.virt_in, "gain", 5.8),
        ],
    )
    def test_it_sets_and_gets_strip_float_params(self, index, param, value):
        setattr(tests.strip[index], param, value)
        assert getattr(tests.strip[index], param) == value

    @pytest.mark.parametrize(
        "index,value",
        [(data.phys_in, 2), (data.phys_in, 2), (data.virt_in, 8), (data.virt_in, 8)],
    )
    def test_it_gets_prefader_levels_and_compares_length_of_array(self, index, value):
        assert len(tests.strip[index].levels.prefader) == value

    @pytest.mark.skipif(
        data.name != "potato",
        reason="Only test if logged into Potato version",
    )
    @pytest.mark.parametrize(
        "index, j, value",
        [
            (data.phys_in, 0, -20.7),
            (data.virt_in, 3, -60),
            (data.virt_in, 4, 3.6),
            (data.phys_in, 4, -12.7),
        ],
    )
    def test_it_sets_and_gets_strip_gainlayer_values(self, index, j, value):
        tests.strip[index].gainlayer[j].gain = value
        assert tests.strip[index].gainlayer[j].gain == value

    """ strip tests, virtual """

    @pytest.mark.parametrize(
        "index, param, value",
        [
            (data.virt_in, "treble", -1.6),
            (data.virt_in, "mid", 5.8),
            (data.virt_in, "bass", -8.1),
        ],
    )
    def test_it_sets_and_gets_strip_eq_params(self, index, param, value):
        setattr(tests.strip[index], param, value)
        assert getattr(tests.strip[index], param) == value

    """ bus tests, physical and virtual """

    @pytest.mark.parametrize(
        "index, param, value",
        [(data.phys_out, "gain", -3.6), (data.virt_out, "gain", 5.8)],
    )
    def test_it_sets_and_gets_bus_float_params(self, index, param, value):
        setattr(tests.bus[index], param, value)
        assert getattr(tests.bus[index], param) == value

    @pytest.mark.parametrize(
        "index,value",
        [(data.phys_out, 8), (data.virt_out, 8)],
    )
    def test_it_gets_prefader_levels_and_compares_length_of_array(self, index, value):
        assert len(tests.bus[index].levels.all) == value


@pytest.mark.parametrize("value", ["test0", "test1"])
class TestSetAndGetStringHigher:
    __test__ = True

    """strip tests, physical and virtual"""

    @pytest.mark.parametrize(
        "index, param",
        [(data.phys_in, "label"), (data.virt_in, "label")],
    )
    def test_it_sets_and_gets_strip_string_params(self, index, param, value):
        setattr(tests.strip[index], param, value)
        assert getattr(tests.strip[index], param) == value

    """ bus tests, physical and virtual """

    @pytest.mark.parametrize(
        "index, param",
        [(data.phys_out, "label"), (data.virt_out, "label")],
    )
    def test_it_sets_and_gets_bus_string_params(self, index, param, value):
        setattr(tests.bus[index], param, value)
        assert getattr(tests.bus[index], param) == value
