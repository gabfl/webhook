import unittest
import tempfile
import os

import pytest

from .. import app, bootstrap, routes_handler


class Test(unittest.TestCase):

    def setUp(self):
        self.app = bootstrap.get_or_create_app()
        self.db_fd, self.app.config['DATABASE'] = tempfile.mkstemp()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.app.config['DATABASE'])

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

    def test_new_json(self):
        rv = self.client.get('/new/json')
        assert rv.status_code == 200
        assert 'application/json' in rv.headers['Content-Type']
        self.assertIsInstance(rv.json['routes'], dict)
        self.assertIsInstance(rv.json['routes']['inspect'], dict)
        self.assertIsInstance(rv.json['routes']['inspect']['html'], str)
        self.assertIsInstance(rv.json['routes']['inspect']['json'], str)

    def test_new_2(self):
        rv = self.client.get('/new', follow_redirects=True)
        assert rv.status_code == 200
        assert b'Current route' in rv.data

    def test_inspect_as_html(self):
        # Generate a new path
        path = routes_handler.new()

        rv = self.client.get('/' + path + '/inspect')
        assert rv.status_code == 200
        assert b'Current route' in rv.data

    def test_inspect_as_html_with_callbacks_json(self):
        # Generate a new path
        path = routes_handler.new()

        # Try sending some data to the webhook URL
        self.client.post('/' + path, json={
            'hello': 'world',
            'find_me': 'looking for this string'
        })

        rv = self.client.get('/' + path + '/inspect')
        assert rv.status_code == 200
        assert b'Current route' in rv.data
        assert b'looking for this string' in rv.data

    def test_inspect_as_html_with_callbacks_get(self):
        # Generate a new path
        path = routes_handler.new()

        # Try sending some data to the webhook URL
        self.client.get('/' + path + '?some_var=looking-for-this-string')

        rv = self.client.get('/' + path + '/inspect')
        assert rv.status_code == 200
        assert b'Current route' in rv.data
        assert b'looking-for-this-string' in rv.data

    def test_inspect_as_html_with_callbacks_data(self):
        # Generate a new path
        path = routes_handler.new()

        # Try sending some data to the webhook URL
        self.client.post('/' + path, data=dict(
            hello='a',
            find_me='looking for this string'
        ))

        rv = self.client.get('/' + path + '/inspect')
        assert rv.status_code == 200
        assert b'Current route' in rv.data
        assert b'looking+for+this+string' in rv.data

    def test_inspect_as_json(self):
        # Generate a new path
        path = routes_handler.new()

        rv = self.client.get('/' + path + '/inspect/json')
        assert rv.status_code == 200
        assert 'application/json' in rv.headers['Content-Type']
        self.assertIsInstance(rv.json, dict)
        assert 'callbacks' in rv.json
        assert 'routes' in rv.json
        assert 'creation_date' in rv.json
        self.assertIsInstance(rv.json['callbacks'], list)
        self.assertIsInstance(rv.json['routes'], dict)
        self.assertIsInstance(rv.json['routes']['inspect'], dict)
        self.assertIsInstance(rv.json['routes']['inspect']['html'], str)
        self.assertIsInstance(rv.json['routes']['inspect']['json'], str)
        self.assertIsInstance(rv.json['routes']['webhook'], str)
        self.assertIsInstance(rv.json['creation_date'], str)

    def test_inspect_as_json_with_callbacks_json(self):
        # Generate a new path
        path = routes_handler.new()

        # Try sending some data to the webhook URL
        self.client.post('/' + path, json={
            'hello': 'world',
            'find_me': 'looking for this string'
        })

        rv = self.client.get('/' + path + '/inspect/json')
        assert rv.status_code == 200
        assert 'application/json' in rv.headers['Content-Type']
        assert 'callbacks' in rv.json
        self.assertIsInstance(rv.json['callbacks'], list)
        for callback in rv.json['callbacks']:
            self.assertIsInstance(callback['body'], dict)
            self.assertIsInstance(callback['body']['data'], dict)
            self.assertIsInstance(callback['body']['size'], int)

    def test_inspect_as_json_with_callbacks_get(self):
        # Generate a new path
        path = routes_handler.new()

        # Try sending some data to the webhook URL
        self.client.get('/' + path + '?some_var=looking-for-this-string')

        rv = self.client.get('/' + path + '/inspect/json')
        assert rv.status_code == 200
        assert 'application/json' in rv.headers['Content-Type']
        assert 'callbacks' in rv.json
        self.assertIsInstance(rv.json['callbacks'], list)
        for callback in rv.json['callbacks']:
            self.assertIsInstance(callback['args'], dict)
            self.assertIsInstance(callback['body'], dict)
            self.assertIsNone(callback['body']['data'])
            assert callback['body']['size'] == 0

    def test_inspect_as_json_with_callbacks_data(self):
        # Generate a new path
        path = routes_handler.new()

        # Try sending some data to the webhook URL
        self.client.post('/' + path, data=dict(
            hello='a',
            find_me='looking for this string'
        ))

        rv = self.client.get('/' + path + '/inspect/json')
        assert rv.status_code == 200
        assert 'application/json' in rv.headers['Content-Type']
        assert 'callbacks' in rv.json
        self.assertIsInstance(rv.json['callbacks'], list)
        for callback in rv.json['callbacks']:
            self.assertIsInstance(callback['body'], dict)
            self.assertIsInstance(callback['body']['data'], str)
            self.assertIsInstance(callback['body']['size'], int)

    def test_callback_get(self):
        # Generate a new path
        path = routes_handler.new()

        rv = self.client.get('/' + path)
        assert rv.status_code == 200
        assert rv.data == b'OK'

    def test_callback_post(self):
        # Generate a new path
        path = routes_handler.new()

        rv = self.client.post('/' + path)
        assert rv.status_code == 200
        assert rv.data == b'OK'

    def test_callback_put(self):
        # Generate a new path
        path = routes_handler.new()

        rv = self.client.put('/' + path)
        assert rv.status_code == 200
        assert rv.data == b'OK'

    def test_callback_delete(self):
        # Generate a new path
        path = routes_handler.new()

        rv = self.client.delete('/' + path)
        assert rv.status_code == 200
        assert rv.data == b'OK'

    def test_callback_invalid(self):
        rv = self.client.get('/some_bad_route')
        # Should be a 307 to redirect to 404
        assert rv.status_code == 307
        assert b'You should be redirected automatically' in rv.data
        assert b'/404' in rv.data

    def test_abort_404_2(self):
        rv = self.client.get('/404')
        assert rv.status_code == 404
