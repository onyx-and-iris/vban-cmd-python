from nose.tools import assert_equal, nottest
from parameterized import parameterized, parameterized_class

import unittest
from tests import tests

#@nottest
@parameterized_class([
    { "val": False }, { "val": True }
])
class TestSetAndGetBoolHigher(unittest.TestCase):
    """ strip tests, physical and virtual """
    @parameterized.expand([
    (0, 'mute'), (2, 'mono'), (3, 'A1'), (3, 'B3')
    ])
    def test_it_sets_and_gets_strip_bool_params(self, index, param):
        setattr(tests.strip[index], param, self.val)
        retval = getattr(tests.strip[index], param)
        self.assertTrue(isinstance(retval, bool))
        assert_equal(retval, self.val)


#@nottest
@parameterized_class([
    { "val": "test0" }, { "val": "test1" }
])
class TestSetAndGetStringHigher(unittest.TestCase):
    """ strip tests, physical and virtual """
    @parameterized.expand([
    (2, 'label'), (3, 'label')
    ])
    def test_it_sets_and_gets_strip_string_params(self, index, param):
        setattr(tests.strip[index], param, self.val)
        assert_equal(getattr(tests.strip[index], param), self.val)

    """ bus tests, physical and virtual """
    @parameterized.expand([
    (0, 'label'), (4, 'label')
    ])
    def test_it_sets_and_gets_bus_string_params(self, index, param):
        setattr(tests.bus[index], param, self.val)
        assert_equal(getattr(tests.bus[index], param), self.val)
