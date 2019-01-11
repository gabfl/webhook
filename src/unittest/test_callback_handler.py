import uuid

from .base import BaseTest
from .. import callback_handler
from ..models import db, RouteModel, CallbackModel


class Test(BaseTest):

    def tearDown(self):
        RouteModel.query.delete()
        CallbackModel.query.delete()
        db.session.commit()

    def test_get_callbacks(self):

        # Create a route
        route = RouteModel(path=str(uuid.uuid4()))
        db.session.add(route)

        db.session.commit()

        # Add some callback rows
        route_callbacks = [
            CallbackModel(route_id=route.id),
            CallbackModel(route_id=route.id)
        ]
        db.session.add_all([callback for callback in route_callbacks])

        db.session.commit()

        callbacks = callback_handler.get_callbacks(route.id)

        self.assertIsInstance(callbacks, list)
        for callback in callbacks:
            assert 'id' in callback
            assert 'headers' in callback
            assert 'method' in callback
            assert 'args' in callback
            assert 'body' in callback
            assert 'date' in callback
            assert 'referrer' in callback
            assert 'remote_addr' in callback

    def test_get_callbacks_cursor(self):

        # Create a route
        route = RouteModel(path=str(uuid.uuid4()))
        db.session.add(route)

        db.session.commit()

        # Add 60 callback rows
        route_callbacks = []
        for idx in range(0, 60):
            route_callbacks.append(CallbackModel(route_id=route.id))
        db.session.add_all([callback for callback in route_callbacks])

        db.session.commit()

        # Initial call
        callbacks = callback_handler.get_callbacks(route.id)
        cursor = callback_handler.get_cursor(callbacks)
        self.assertIsInstance(callbacks, list)
        self.assertIsInstance(cursor, int)
        assert len(callbacks) == 50

        # subsequent call
        callbacks = callback_handler.get_callbacks(route.id, cursor=cursor)
        self.assertIsInstance(callbacks, list)
        assert len(callbacks) == 10

    def test_is_json(self):
        assert callback_handler.is_json('abc') is False

    def test_is_json_2(self):
        assert callback_handler.is_json('{"a": true, "b": false}') is True
