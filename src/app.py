import json
import os

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify

from .bootstrap import get_or_create_app
from . import callback_handler
from . import routes_handler
from .models import db, RouteModel, CallbackModel


app = get_or_create_app()


@app.route("/")
def hp():
    return render_template('index.html', host_url=request.host_url)


@app.route("/robots.txt")
def robots():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'robots.txt', mimetype='text/plain')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/x-icon')


@app.route("/new")
def new():
    # Cleanup old routes
    routes_handler.cleanup_old_routes()

    # Generate a new route
    route = routes_handler.new()

    return redirect('/' + route.path + '/inspect'), 307


@app.route("/api/new")
def new_json():
    # Generate a new route
    route = routes_handler.new()

    return jsonify({
        'routes': {
            'inspect': {
                'html': request.host_url + route.path + '/inspect',
                'json': request.host_url + 'api/' + route.path + '/inspect'
            },
            'webhook': request.host_url + route.path
        },
    })


@app.route('/<string:route_path>/inspect', methods=['GET'])
def inspect(route_path):
    # Lookup route
    route = RouteModel.query.filter_by(path=route_path).first()

    # Return 404 if unknown route
    if not route:
        return redirect(url_for('abort_404')), 307

    # Get callbacks
    callbacks = callback_handler.get_callbacks(
        route.id, cursor=request.args.get('cursor'))

    return render_template(
        'inspect.html',
        route_path=route_path,
        callbacks=callbacks,
        cursor=callback_handler.get_cursor(callbacks),
        host_url=request.host_url
    )


@app.route('/api/<string:route_path>/inspect', methods=['GET'])
def inspect_json(route_path):
    # Lookup route
    route = RouteModel.query.filter_by(path=route_path).first()

    # Return 404 if unknown route
    if not route:
        return jsonify({
            'message': "Invalid route"
        }), 404

    # Get callbacks
    callbacks = callback_handler.get_callbacks(
        route.id, cursor=request.args.get('cursor'))
    cursor = callback_handler.get_cursor(callbacks)

    return jsonify({
        'routes': {
            'inspect': {
                'html': request.host_url + route_path + '/inspect',
                'json': request.host_url + 'api/' + route_path + '/inspect'
            },
            'webhook': request.host_url + route_path
        },
        'callbacks': callbacks,
        'creation_date': route.creation_date,
        'expiration_date': route.expiration_date,
        'next': request.host_url + 'api/' + route_path + '/inspect?cursor=' + str(cursor) if cursor else None
    })


@app.route('/<string:route_path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def callback(route_path):
    # Lookup route
    route = RouteModel.query.filter_by(path=route_path).first()

    # Return 404 if unknown route
    if not route:
        return redirect(url_for('abort_404')), 307

    # Save callback
    callback_handler.save(route.id)

    return 'OK'


@app.route("/404")
def abort_404():
    return render_template('404.html'), 404
