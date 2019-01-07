import unittest
import uuid

from .. import callback_handler
from ..models import db, RouteModel, CallbackModel


class Test(unittest.TestCase):

    route = None
    route_callback_1 = None
    route_callback_2 = None

    def test_get_callbacks(self):

        # Create 2 routes, one expired
        self.route = RouteModel(path=str(uuid.uuid4()))
        db.session.add(self.route)

        db.session.commit()

        # Add some callback rows
        self.route_callback_1 = CallbackModel(
            route_id=self.route.id)
        db.session.add(self.route_callback_1)
        self.route_callback_2 = CallbackModel(
            route_id=self.route.id)
        db.session.add(self.route_callback_2)

        db.session.commit()

        callbacks = callback_handler.get_callbacks(self.route.id)

        self.assertIsInstance(callbacks, list)
        for callback in callbacks:
            assert 'headers' in callback
            assert 'method' in callback
            assert 'args' in callback
            assert 'body' in callback
            assert 'date' in callback
            assert 'referrer' in callback
            assert 'remote_addr' in callback

    def test_is_json(self):
        assert callback_handler.is_json('abc') is False

    def test_is_json_2(self):
        assert callback_handler.is_json('{"a": true, "b": false}') is True
