
from .base import BaseTest
from .. import setup


class Test(BaseTest):

    def test_setup(self):
        assert setup.setup() is True
