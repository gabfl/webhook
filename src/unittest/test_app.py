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

    def test_new(self):
        rv = self.client.get('/new')
        assert rv.status_code == 307

    def test_new_2(self):
        rv = self.client.get('/new', follow_redirects=True)
        assert rv.status_code == 200
        assert b'Current route' in rv.data

    def test_catch_all_get(self):
        # Generate a new path
        path = routes_handler.new()

        rv = self.client.get('/' + path)
        assert rv.status_code == 200
        assert rv.data == b'OK'

    def test_catch_all_post(self):
        # Generate a new path
        path = routes_handler.new()

        rv = self.client.post('/' + path)
        assert rv.status_code == 200
        assert rv.data == b'OK'

    def test_catch_all_put(self):
        # Generate a new path
        path = routes_handler.new()

        rv = self.client.put('/' + path)
        assert rv.status_code == 200
        assert rv.data == b'OK'

    def test_catch_all_delete(self):
        # Generate a new path
        path = routes_handler.new()

        rv = self.client.delete('/' + path)
        assert rv.status_code == 200
        assert rv.data == b'OK'

    def test_catch_all_inspect(self):
        # Generate a new path
        path = routes_handler.new()

        rv = self.client.get('/' + path + '/inspect')
        assert rv.status_code == 200
        assert b'Current route' in rv.data

    def test_catch_all_inspect_with_callbacks_json(self):
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

    def test_catch_all_inspect_with_callbacks_not_json(self):
        # Generate a new path
        path = routes_handler.new()

        # Try sending some data to the webhook URL
        self.client.get('/' + path + '?some_var=looking-for-this-string')

        rv = self.client.get('/' + path + '/inspect', follow_redirects=True)
        assert rv.status_code == 200
        assert b'Current route' in rv.data
        # assert b'looking-for-this-string' in rv.data

    def test_abort_404(self):
        rv = self.client.get('/some_bad_route')
        # Should be a 307 to redirect to 404
        assert rv.status_code == 307

    def test_abort_404_2(self):
        rv = self.client.get('/404')
        assert rv.status_code == 404
