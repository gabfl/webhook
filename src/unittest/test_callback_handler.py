import unittest

from .. import callback_handler


class Test(unittest.TestCase):

    def test_is_json(self):
        assert callback_handler.is_json('abc') is False

    def test_is_json_2(self):
        assert callback_handler.is_json('{"a": true, "b": false}') is True
