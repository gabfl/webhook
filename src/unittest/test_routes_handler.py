import unittest
import uuid
from dateparser import parse

from .. import routes_handler
from ..models import db, RouteModel, CallbackModel


class Test(unittest.TestCase):

    route_1 = None
    route_2 = None
    route_1_callback_1 = None
    route_1_callback_2 = None
    route_2_callback_1 = None
    route_2_callback_2 = None

    def tearDown(self):
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

        route_path = routes_handler.new()

        # Lookup route
        self.route_1 = RouteModel.query.filter_by(route=route_path).first()

        self.assertIsInstance(self.route_1.id, int)
        assert self.route_1.route == route_path
        assert len(self.route_1.route) == 36

    def test_cleanup_old_routes(self):
        # Create 2 routes, one expired
        self.route_1 = RouteModel(route=str(uuid.uuid4()), )
        db.session.add(self.route_1)
        self.route_2 = RouteModel(route=str(uuid.uuid4()),
                                  creation_date=parse('1 month ago'))
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
            route=self.route_1.route).first(), RouteModel)

        callbacks = CallbackModel.query.filter_by(
            route_id=self.route_1.id).all()
        self.assertIsInstance(callbacks, list)
        assert len(callbacks) == 2
        for callback in callbacks:
            self.assertIsInstance(callback, CallbackModel)

        # Second route and it's callback should be deleted
        self.assertIsNone(RouteModel.query.filter_by(
            route=self.route_2.route).first())

        callbacks = CallbackModel.query.filter_by(
            route_id=self.route_2.id).all()
        self.assertIsInstance(callbacks, list)
        assert len(callbacks) == 0
