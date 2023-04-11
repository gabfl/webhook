
from datetime import datetime

from .base import BaseTest
from .. import app, bootstrap, routes_handler
from ..bootstrap import get_or_create_app


class Test(BaseTest):

    def setUp(self):
        self.app = get_or_create_app()

    def test__jinja2_filter_datetime(self):
        """
            Test Jinja custom filter that converts a date
            from UTC to local TZ and returns output as a str
        """

        dt = datetime(2020, 2, 26, 19, 42, 23, 824725)
        assert app._jinja2_filter_datetime(
            dt) == 'February 26, 2020 02:42:23 PM'

    def test__jinja2_filter_datetime_2(self):
        """
            Test Jinja custom filter that converts a date
            from UTC to local TZ and returns output as a str
            with a custom format
        """

        dt = datetime(2020, 2, 26, 19, 42, 23, 824725)
        assert app._jinja2_filter_datetime(
            dt, fmt='%B %d, %Y') == 'February 26, 2020'

    def test_hp(self):
        rv = self.client.get('/')
        assert rv.status_code == 200
        assert 'text/html' in rv.headers['Content-Type']

    def test_robots_txt(self):
        rv = self.client.get('/robots.txt')
        assert rv.status_code == 200
        assert b'User-Agent' in rv.data
        assert 'text/plain' in rv.headers['Content-Type']

    def test_favicon_ico(self):
        rv = self.client.get('/favicon.ico')
        assert rv.status_code == 200
        assert 'image/x-icon' in rv.headers['Content-Type']

    def test_new(self):
        rv = self.client.get('/new')
        assert rv.status_code == 307
        assert 'text/html' in rv.headers['Content-Type']

    def test_new_2(self):
        rv = self.client.get('/new', follow_redirects=True)
        assert rv.status_code == 200
        assert b'Current route' in rv.data

    def test_api_new(self):
        rv = self.client.get('/api/new')
        assert rv.status_code == 200
        assert 'application/json' in rv.headers['Content-Type']
        self.assertIsInstance(rv.json['routes'], dict)
        self.assertIsInstance(rv.json['routes']['inspect'], dict)
        self.assertIsInstance(rv.json['routes']['inspect']['html'], str)
        self.assertIsInstance(rv.json['routes']['inspect']['api'], str)

    def test_api_delete_route(self):
        with self.app.app_context():
            # Generate a new path
            route = routes_handler.new()
            path = route.path

            rv = self.client.get('/api/delete/' + path)
            assert 'application/json' in rv.headers['Content-Type']
            assert rv.status_code == 200
            assert rv.json['message'] == 'The route has been deleted'

    def test_api_delete_route_2(self):
        rv = self.client.get('/api/delete/some_bad_route')
        assert 'application/json' in rv.headers['Content-Type']
        assert rv.status_code == 404
        assert rv.json['message'] == 'Invalid route'

    def test_inspect(self):
        with self.app.app_context():
            # Generate a new path
            route = routes_handler.new()
            path = route.path

            rv = self.client.get('/inspect/' + path)
            assert rv.status_code == 200
            assert b'Current route' in rv.data
            # There should not be a next page of results
            assert b'Previous results' not in rv.data

    def test_inspect_cursor(self):
        with self.app.app_context():
            # Generate a new path
            route = routes_handler.new()
            path = route.path

            # Generate 60 callbacks
            for i in range(60):
                self.client.get('/' + path)

            rv = self.client.get('/inspect/' + path)
            assert rv.status_code == 200
            assert b'Current route' in rv.data
            # There should be a next page of results
            assert b'Previous results' in rv.data

    def test_inspect_with_callbacks_json(self):
        with self.app.app_context():
            # Generate a new path
            route = routes_handler.new()
            path = route.path

            # Try sending some data to the webhook URL
            self.client.post('/' + route.path, json={
                'hello': 'world',
                'find_me': 'looking for this string'
            })

            rv = self.client.get('/inspect/' + path)
            assert rv.status_code == 200
            assert b'Current route' in rv.data
            assert b'looking for this string' in rv.data

    def test_inspect_with_callbacks_get(self):
        with self.app.app_context():
            # Generate a new path
            route = routes_handler.new()
            path = route.path

            # Try sending some data to the webhook URL
            self.client.get('/' + path + '?some_var=looking-for-this-string')

            rv = self.client.get('/inspect/' + path)
            assert rv.status_code == 200
            assert b'Current route' in rv.data
            assert b'looking-for-this-string' in rv.data

    def test_inspect_with_callbacks_data(self):
        with self.app.app_context():
            # Generate a new path
            route = routes_handler.new()
            path = route.path

            # Try sending some data to the webhook URL
            self.client.post('/' + path, data=dict(
                hello='a',
                find_me='looking for this string'
            ))

            rv = self.client.get('/inspect/' + path)
            assert rv.status_code == 200
            assert b'Current route' in rv.data
            assert b'looking+for+this+string' in rv.data

    def test_inspect_rename(self):
        with self.app.app_context():
            # Generate a new path
            route = routes_handler.new()
            path = route.path

            # Sending a POST with a new webhook name
            rv = self.client.post('/inspect/' + path, data=dict(
                set_name='New route name'
            ))

            assert rv.status_code == 200
            assert b'New route name' in rv.data

    def test_inspect_invalid(self):
        rv = self.client.get('/inspect/some_bad_route')
        # Should be a 307 to redirect to 404
        assert rv.status_code == 307
        assert b'You should be redirected automatically' in rv.data
        assert b'/404' in rv.data

    def test_api_inspect(self):
        with self.app.app_context():
            # Generate a new path
            route = routes_handler.new()
            path = route.path

            rv = self.client.get('/api/inspect/' + path)
            assert rv.status_code == 200
            assert 'application/json' in rv.headers['Content-Type']
            self.assertIsInstance(rv.json, dict)
            assert 'callbacks' in rv.json
            assert 'routes' in rv.json
            self.assertIsInstance(rv.json['callbacks'], list)
            self.assertIsInstance(rv.json['routes'], dict)
            self.assertIsInstance(rv.json['routes']['inspect'], dict)
            self.assertIsInstance(rv.json['routes']['inspect']['html'], str)
            self.assertIsInstance(rv.json['routes']['inspect']['api'], str)
            self.assertIsInstance(rv.json['routes']['delete'], dict)
            self.assertIsInstance(rv.json['routes']['delete']['api'], str)
            self.assertIsInstance(rv.json['routes']['webhook'], str)
            self.assertIsInstance(rv.json['creation_date'], str)
            self.assertIsInstance(rv.json['expiration_date'], str)
            self.assertIsNone(rv.json['name'])
            self.assertIsNone(rv.json['next'])

    def test_api_inspect_cursor(self):
        with self.app.app_context():
            # Generate a new path
            route = routes_handler.new()
            path = route.path

            # Generate 60 callbacks
            for i in range(60):
                self.client.get('/' + path)

            rv = self.client.get('/api/inspect/' + path)
            assert rv.status_code == 200
            assert 'application/json' in rv.headers['Content-Type']

            # Ensure that we have a URL for the next results
            self.assertIsInstance(rv.json['next'], str)

            # Load the next page of results
            rv = self.client.get(rv.json['next'])
            assert rv.status_code == 200
            assert 'application/json' in rv.headers['Content-Type']

            # Ensure that we have an empty field for the next page
            self.assertIsNone(rv.json['next'])

    def test_api_inspect_with_callbacks_json(self):
        with self.app.app_context():
            # Generate a new path
            route = routes_handler.new()
            path = route.path

            # Try sending some data to the webhook URL
            self.client.post('/' + path, json={
                'hello': 'world',
                'find_me': 'looking for this string'
            })

            rv = self.client.get('/api/inspect/' + path)
            assert rv.status_code == 200
            assert 'application/json' in rv.headers['Content-Type']
            assert 'callbacks' in rv.json
            self.assertIsInstance(rv.json['callbacks'], list)
            for callback in rv.json['callbacks']:
                self.assertIsInstance(callback['body'], dict)
                self.assertIsInstance(callback['body']['data'], dict)
                self.assertIsInstance(callback['body']['size'], int)
                self.assertIsInstance(callback['routes'], dict)
                self.assertIsInstance(callback['routes']['delete'], str)

    def test_api_inspect_with_callbacks_get(self):
        with self.app.app_context():
            # Generate a new path
            route = routes_handler.new()
            path = route.path

            # Try sending some data to the webhook URL
            self.client.get('/' + path + '?some_var=looking-for-this-string')

            rv = self.client.get('/api/inspect/' + path)
            assert rv.status_code == 200
            assert 'application/json' in rv.headers['Content-Type']
            assert 'callbacks' in rv.json
            self.assertIsInstance(rv.json['callbacks'], list)
            for callback in rv.json['callbacks']:
                self.assertIsInstance(callback['args'], dict)
                self.assertIsInstance(callback['body'], dict)
                self.assertIsNone(callback['body']['data'])
                assert callback['body']['size'] == 0

    def test_api_inspect_with_callbacks_data(self):
        with self.app.app_context():
            # Generate a new path
            route = routes_handler.new()
            path = route.path

            # Try sending some data to the webhook URL
            self.client.post('/' + path, data=dict(
                hello='a',
                find_me='looking for this string'
            ))

            rv = self.client.get('/api/inspect/' + path)
            assert rv.status_code == 200
            assert 'application/json' in rv.headers['Content-Type']
            assert 'callbacks' in rv.json
            self.assertIsInstance(rv.json['callbacks'], list)
            for callback in rv.json['callbacks']:
                self.assertIsInstance(callback['body'], dict)
                self.assertIsInstance(callback['body']['data'], str)
                self.assertIsInstance(callback['body']['size'], int)

    def test_api_inspect_invalid(self):
        rv = self.client.get('/api/inspect/some_bad_route')
        assert rv.status_code == 404
        assert rv.json['message'] == 'Invalid route'

    def test_api_delete_callback(self):
        with self.app.app_context():
            # Generate a new path
            route = routes_handler.new()
            path = route.path

            # Generate a callback
            self.client.get('/' + path)

            # Call the inspect endpoint
            rv = self.client.get('/api/inspect/' + path)
            callback_id = rv.json['callbacks'][0]['id']

            # Call the callback deletion endpoint
            rv = self.client.get(
                '/api/delete/' + path + '/' + str(callback_id)
            )
            assert 'application/json' in rv.headers['Content-Type']
            assert rv.status_code == 200
            assert rv.json['message'] == 'The webhook has been deleted'

            # We should obtain an error if we call the same route again
            rv = self.client.get(
                '/api/delete/' + path + '/' + str(callback_id)
            )
            assert 'application/json' in rv.headers['Content-Type']
            assert rv.status_code == 400
            assert rv.json['message'] == 'Invalid route or callback ID'

    def test_api_delete_callback_2(self):
        rv = self.client.get('/api/delete/some_bad_route/1')
        assert 'application/json' in rv.headers['Content-Type']
        assert rv.status_code == 404
        assert rv.json['message'] == 'Invalid route'

    def test_callback_get(self):
        with self.app.app_context():
            # Generate a new path
            route = routes_handler.new()
            path = route.path

            rv = self.client.get('/' + path)
            assert rv.status_code == 200
            assert rv.data == b'OK'

    def test_callback_post(self):
        with self.app.app_context():
            # Generate a new path
            route = routes_handler.new()
            path = route.path

            rv = self.client.post('/' + path)
            assert rv.status_code == 200
            assert rv.data == b'OK'

    def test_callback_put(self):
        with self.app.app_context():
            # Generate a new path
            route = routes_handler.new()
            path = route.path

            rv = self.client.put('/' + path)
            assert rv.status_code == 200
            assert rv.data == b'OK'

    def test_callback_delete(self):
        with self.app.app_context():
            # Generate a new path
            route = routes_handler.new()
            path = route.path

            rv = self.client.delete('/' + path)
            assert rv.status_code == 200
            assert rv.data == b'OK'

    def test_callback_invalid(self):
        rv = self.client.get('/some_bad_route')
        # Should be a 307 to redirect to 404
        assert rv.status_code == 307
        assert b'You should be redirected automatically' in rv.data
        assert b'/404' in rv.data

    def test_abort_404(self):
        rv = self.client.get('/404')
        assert rv.status_code == 404
