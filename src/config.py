import configparser
import os
from uuid import uuid4

dir_path = os.path.dirname(os.path.realpath(__file__))
config_path = dir_path + '/../webhook.cfg'

# Config
config = configparser.ConfigParser()


def get_config():
    """
        Will return a user config and set a default if necessary
    """

    # Generate a default config the first time
    if not os.path.isfile(config_path):
        return

    # Load existing config
    config.read(config_path)
    return config['MAIN']


def __getattr__(name):
    """
        Allows calls to configuration values:
        config = Config()
        print(config.salt) # Will print the salt
    """

    config = get_config()

    # No config file
    if config is None:
        return

    try:
        return config[name]
    except KeyError:  # For values that don't exist in the config file
        return
