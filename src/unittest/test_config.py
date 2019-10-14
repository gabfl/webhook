import configparser

from .base import BaseTest
from .. import config


class Test(BaseTest):

    def test_get_config(self):
        assert isinstance(config.get_config(), configparser.SectionProxy)

    def test_get_config_2(self):
        # Test with non-existing config file

        old_path = config.config_path
        config.config_path = '/dev/null/void'
        assert config.get_config() is None

        # Restore path
        config.config_path = old_path

    def test_getattr(self):

        assert isinstance(config.webhook_expire, str)
        assert config.non_existant is None

    def test_getattr_2(self):
        # Test getting a value with a non-existing config file

        old_path = config.config_path
        config.config_path = '/dev/null/void'

        assert config.webhook_expire is None

        # Restore path
        config.config_path = old_path
