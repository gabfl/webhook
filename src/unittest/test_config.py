import configparser

from .base import BaseTest
from ..config import Config


class Test(BaseTest):

    def test_get_config(self):
        conf = Config()

        assert isinstance(conf.get_config(), configparser.SectionProxy)

    def test_get_config_2(self):
        # Test with non-existing config file

        conf = Config()

        #old_path = config.config_path
        conf.config_path = '/dev/null/void'
        assert conf.get_config() is None

        # Restore path
        #config.config_path = old_path

    def test_getattr(self):

        conf = Config()

        assert isinstance(conf.webhook_expire, str)
        assert conf.non_existant is None

    def test_getattr_2(self):
        # Test getting a value with a non-existing config file

        #old_path = config.config_path
        conf = Config()

        conf.config_path = '/dev/null/void'

        assert conf.webhook_expire is None

        # Restore path
       # config.config_path = old_path
