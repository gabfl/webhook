import uuid

from dateparser import parse

from .base import BaseTest
from .. import routes_handler
from ..models import db, RouteModel, CallbackModel
from ..bootstrap import get_or_create_app


class Test(BaseTest):

    route_1 = None
    route_2 = None
    route_1_callback_1 = None
    route_1_callback_2 = None
    route_2_callback_1 = None
    route_2_callback_2 = None

    def setUp(self):
        self.app = get_or_create_app()

    def tearDown(self):
        with self.app.app_context():
            if self.route_1:
                db.session.delete(self.route_1)
            if self.route_2:
                db.session.delete(self.route_2)
            if self.route_1_callback_1:
                db.session.delete(self.route_1_callback_1)
            if self.route_1_callback_2:
                db.session.delete(self.route_1_callback_2)
            if self.route_2_callback_1:
                db.session.delete(self.route_2_callback_1)
            if self.route_2_callback_2:
                db.session.delete(self.route_2_callback_2)
            db.session.commit()

    def test_new(self):
        with self.app.app_context():
            route = routes_handler.new()

            self.assertIsInstance(route, RouteModel)
            self.assertIsInstance(route.id, int)
            self.assertIsInstance(route.path, str)
            assert len(route.path) == 36

    def test_rename(self):
        with self.app.app_context():
            route = routes_handler.new()

            # Default name should be None
            assert route.name is None

            # Rename route with empty name
            routes_handler.rename(route, '')
            assert route.name is None

            # Rename route with a valid name
            routes_handler.rename(route, 'New route name')
            assert route.name == 'New route name'

    def test_cleanup_old_routes(self):
        with self.app.app_context():
            # Create 2 routes, one expired
            self.route_1 = RouteModel(path=str(uuid.uuid4()), )
            db.session.add(self.route_1)
            self.route_2 = RouteModel(path=str(uuid.uuid4()),
                                      expiration_date=parse('1 month ago'))
            db.session.add(self.route_2)

            db.session.commit()

            # Add some callback rows
            self.route_1_callback_1 = CallbackModel(route_id=self.route_1.id)
            db.session.add(self.route_1_callback_1)
            self.route_1_callback_2 = CallbackModel(route_id=self.route_1.id)
            db.session.add(self.route_1_callback_2)
            self.route_2_callback_1 = CallbackModel(route_id=self.route_2.id)
            db.session.add(self.route_2_callback_1)
            self.route_2_callback_2 = CallbackModel(route_id=self.route_2.id)
            db.session.add(self.route_2_callback_2)

            db.session.commit()

            # Call cleanup method
            routes_handler.cleanup_old_routes()

            # First route and its callback should exist
            self.assertIsInstance(RouteModel.query.filter_by(
                path=self.route_1.path).first(), RouteModel)

            callbacks = CallbackModel.query.filter_by(
                route_id=self.route_1.id).all()
            self.assertIsInstance(callbacks, list)
            assert len(callbacks) == 2
            for callback in callbacks:
                self.assertIsInstance(callback, CallbackModel)

            # Second route and it's callback should be deleted
            assert RouteModel.query.filter_by(
                path=self.route_2.path).first() is None

            callbacks = CallbackModel.query.filter_by(
                route_id=self.route_2.id).all()
            self.assertIsInstance(callbacks, list)
            assert len(callbacks) == 0

            # unset deleted routes
            self.route_2 = None
            self.route_2_callback_1 = None
            self.route_2_callback_2 = None

    def test_delete(self):

        with self.app.app_context():
            # Create 2 routes, one expired
            route = RouteModel(path=str(uuid.uuid4()), )
            db.session.add(route)

            db.session.commit()

            # Add some callback rows
            callback_1 = CallbackModel(route_id=route.id)
            db.session.add(callback_1)
            callback_2 = CallbackModel(route_id=route.id)
            db.session.add(callback_2)

            db.session.commit()

            # Call route deletion method
            routes_handler.delete(route)

            # Verify that the route is deleted
            assert RouteModel.query.filter_by(
                path=route.path).first() is None

            # Verify that the callbacks are deleted
            callbacks = CallbackModel.query.filter_by(
                route_id=route.id).all()
            self.assertIsInstance(callbacks, list)
            assert len(callbacks) == 0
