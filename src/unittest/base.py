import unittest

from .. import app, bootstrap
from ..models import db


class BaseTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = bootstrap.get_or_create_app()
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()
        with cls.app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        pass
