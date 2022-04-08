from nose.tools import assert_equal, nottest
from parameterized import parameterized, parameterized_class

import unittest
from tests import tests

# @nottest
@parameterized_class([{"val": False}, {"val": True}])
class TestSetAndGetBoolHigher(unittest.TestCase):
    """strip tests, physical and virtual"""

    @parameterized.expand(
        [
            (0, "mute"),
            (2, "mono"),
            (3, "A1"),
            (6, "B3"),
            (6, "mute"),
        ]
    )
    def test_it_sets_and_gets_strip_bool_params(self, index, param):
        setattr(tests.strip[index], param, self.val)
        retval = getattr(tests.strip[index], param)
        self.assertTrue(isinstance(retval, bool))
        assert_equal(retval, self.val)

    """ bus tests, physical and virtual """

    @parameterized.expand(
        [(0, "mute"), (2, "mono"), (6, "mute"), (2, "eq"), (7, "eq_ab")]
    )
    def test_it_sets_and_gets_bus_bool_params(self, index, param):
        setattr(tests.bus[index], param, self.val)
        retval = getattr(tests.bus[index], param)
        self.assertTrue(isinstance(retval, bool))
        assert_equal(retval, self.val)

    """ bus mode tests, physical and virtual """

    @parameterized.expand(
        [
            (0, "amix"),
            (0, "tvmix"),
            (2, "composite"),
            (2, "upmix41"),
            (7, "upmix21"),
            (7, "rearonly"),
            (6, "lfeonly"),
            (6, "repeat"),
        ]
    )
    def test_it_sets_and_gets_bus_mode_bool_params(self, index, param):
        setattr(tests.bus[index].mode, param, self.val)
        retval = getattr(tests.bus[index].mode, param)
        self.assertTrue(isinstance(retval, bool))
        assert_equal(retval, self.val)


# @nottest
@parameterized_class([{"val": "test0"}, {"val": "test1"}, {"val": ""}])
class TestSetAndGetStringHigher(unittest.TestCase):
    """strip tests, physical and virtual"""

    @parameterized.expand([(2, "label"), (6, "label")])
    def test_it_sets_and_gets_strip_string_params(self, index, param):
        setattr(tests.strip[index], param, self.val)
        assert_equal(getattr(tests.strip[index], param), self.val)

    """ bus tests, physical and virtual """

    @parameterized.expand([(0, "label"), (7, "label")])
    def test_it_sets_and_gets_bus_string_params(self, index, param):
        setattr(tests.bus[index], param, self.val)
        assert_equal(getattr(tests.bus[index], param), self.val)


# @nottest
class TestSetAndGetFloatHigher(unittest.TestCase):
    """strip tests, physical and virtual"""

    @parameterized.expand(
        [(0, 1, "gain", -6.3), (7, 4, "gain", -12.5), (3, 3, "gain", 3.3)]
    )
    def test_it_sets_and_gets_strip_float_params(self, index, j, param, val):
        setattr(tests.strip[index].gainlayer[j], param, val)
        retval = getattr(tests.strip[index].gainlayer[j], param)
        assert_equal(retval, val)

    """ bus tests, physical and virtual """

    @parameterized.expand([(0, "gain", -6.3), (7, "gain", -12.5), (3, "gain", 3.3)])
    def test_it_sets_and_gets_bus_float_params(self, index, param, val):
        setattr(tests.bus[index], param, val)
        retval = getattr(tests.bus[index], param)
        assert_equal(retval, val)
