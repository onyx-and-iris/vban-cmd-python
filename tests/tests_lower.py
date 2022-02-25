from nose.tools import assert_equal, nottest
from parameterized import parameterized, parameterized_class

import unittest
from tests import tests

#@nottest
@parameterized_class([
    { "val": 0 }, { "val": 1 },
])
class TestSetAndGetParamsLower(unittest.TestCase):
    """ get_rt, set_rt test """
    @parameterized.expand([
    (0, 'mute'), (4, 'mute'),
    ])
    def test_it_sets_and_gets_strip_bool_params(self, index, param):
        tests.set_rt(f'Strip[{index}]', param, self.val)
        retval = tests.get_rt()
        retval = not int.from_bytes(retval.stripstate[index], 'little') & tests._modes._mute == 0
        assert_equal(retval, self.val)

    @parameterized.expand([
    (0, 'mono'), (5, 'mono'),
    ])
    def test_it_sets_and_gets_strip_bool_params(self, index, param):
        tests.set_rt(f'Strip[{index}]', param, self.val)
        retval = tests.get_rt()
        retval = not int.from_bytes(retval.stripstate[index], 'little') & tests._modes._mono == 0
        assert_equal(retval, self.val)
