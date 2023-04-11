import uuid
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

from .base import BaseTest
from .. import models
from ..bootstrap import get_or_create_app


class Test(BaseTest):

    route = None
    callback = None

    def setUp(self):
        self.app = get_or_create_app()

    def tearDown(self):
        with self.app.app_context():
            if self.route:
                models.db.session.delete(self.route)
            if self.callback:
                models.db.session.delete(self.callback)
            models.db.session.commit()

    def test_db(self):
        self.assertIsInstance(models.db, SQLAlchemy)

    def test_db_auto_create(self):
        # The db should exist and the method is expected to return False
        assert models.db_auto_create() is False

    def test_db_auto_create_2(self):
        with self.app.app_context():
            # Drop test table to force a db re-creation
            models.RouteModel.__table__.drop(models.db.engine)
            models.CallbackModel.__table__.drop(models.db.engine)

            # The db will be created and the method is expected to return True
            assert models.db_auto_create() is True

    def test_RouteModel(self):
        with self.app.app_context():
            self.route = models.RouteModel(path=str(uuid.uuid4()))
            models.db.session.add(self.route)
            models.db.session.commit()

            self.assertIsInstance(self.route, models.RouteModel)
            self.assertIsInstance(self.route.id, int)
            self.assertIsInstance(self.route.path, str)
            self.assertIsInstance(self.route.creation_date, datetime)
            self.assertIsInstance(self.route.expiration_date, datetime)
            self.assertIsNone(self.route.name)

    def test_RouteModel_repr(self):
        with self.app.app_context():
            self.route = models.RouteModel(path=str(uuid.uuid4()))
            models.db.session.add(self.route)
            models.db.session.commit()

            assert '<Route' in self.route.__repr__()

    def test_CallbackModel(self):
        with self.app.app_context():
            self.route = models.RouteModel(path=str(uuid.uuid4()))
            models.db.session.add(self.route)
            models.db.session.commit()

            self.callback = models.CallbackModel(route_id=self.route.id)
            models.db.session.add(self.callback)
            models.db.session.commit()

            self.assertIsInstance(self.callback, models.CallbackModel)

    def test_CallbackModel_repr(self):
        with self.app.app_context():
            self.route = models.RouteModel(path=str(uuid.uuid4()))
            models.db.session.add(self.route)
            models.db.session.commit()

            self.callback = models.CallbackModel(route_id=self.route.id)
            models.db.session.add(self.callback)
            models.db.session.commit()

            assert '<Callback' in self.callback.__repr__()
