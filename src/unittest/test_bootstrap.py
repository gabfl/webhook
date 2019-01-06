import unittest

from flask import Flask

from .. import bootstrap


class Test(unittest.TestCase):

    def test_get_or_create_app(self):

        # initial setting
        app = bootstrap.get_or_create_app()
        self.assertIsInstance(app, Flask)

        # retrieving an app already created
        app = bootstrap.get_or_create_app()
        self.assertIsInstance(app, Flask)
