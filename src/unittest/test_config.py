import configparser

from .base import BaseTest
from ..config import Config


class Test(BaseTest):

    def test_get_config(self):

        # Load config class
        conf = Config()

        assert isinstance(conf.get_config(), configparser.SectionProxy)

    def test_get_config_2(self):
        # Test with non-existing config file

        # Load config class
        conf = Config()

        conf.config_path = '/dev/null/void'
        assert conf.get_config() is None

    def test_getattr(self):

        # Load config class
        conf = Config()

        assert isinstance(conf.webhook_expire, str)
        assert isinstance(conf.delete_callback_older_than, str)
        assert conf.non_existant is None

    def test_getattr_2(self):
        # Test getting a value with a non-existing config file

        # Load config class
        conf = Config()

        # Set invalid path
        conf.config_path = '/dev/null/void'

        assert conf.webhook_expire is None
        assert conf.delete_callback_older_than is None
