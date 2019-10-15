import configparser
import os


class Config():

    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path = dir_path + '/../webhook.cfg'

    # Config
    config = configparser.ConfigParser()

    def get_config(self):
        # Read optional user config

        # Generate a default config the first time
        if not os.path.isfile(self.config_path):
            return

        # Load existing config
        self.config.read(self.config_path)
        return self.config['MAIN']

    def __getattr__(self, name):
        # Read any user config value

        config = self.get_config()

        # No config file
        if config is None:
            return

        try:
            return config[name]
        except KeyError:  # For values that don't exist in the config file
            return
