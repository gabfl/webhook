import json
import os
from datetime import timezone
from urllib.parse import urlparse

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify

from .bootstrap import get_or_create_app
from . import callback_handler
from . import routes_handler
from .models import db, RouteModel, CallbackModel


app = get_or_create_app()


@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    """
        Custom Jinja filter to convert UTC date to local TZ
        and return it formatted
    """

    # Convert UTC to local TZ
    date = date.replace(tzinfo=timezone.utc).astimezone(tz=None)

    return date.strftime(fmt) if fmt else date.strftime('%B %d, %Y %I:%M:%S %p')


@app.route("/")
def hp():
    return render_template(
        'index.html',
        host_url=request.host_url,
        host_name=urlparse(request.host_url).netloc
    )


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

    return redirect('/inspect/' + route.path), 307


@app.route("/api/new")
def new_json():
    # Generate a new route
    route = routes_handler.new()

    return jsonify({
        'routes': {
            'inspect': {
                'html': request.host_url + 'inspect/' + route.path,
                'api': request.host_url + 'api/inspect/' + route.path
            },
            'webhook': request.host_url + route.path
        },
    })


@app.route("/api/delete/<string:route_path>")
def delete_route_json(route_path):
    # Lookup route
    route = RouteModel.query.filter_by(path=route_path).first()

    # Return 404 if unknown route
    if not route:
        return jsonify({
            'message': "Invalid route"
        }), 404

    # Delete route and its callbacks
    routes_handler.delete(route)

    return jsonify({
        'message': "The route has been deleted"
    })


@app.route('/inspect/<string:route_path>', methods=['GET', 'POST'])
def inspect(route_path):
    # Lookup route
    route = RouteModel.query.filter_by(path=route_path).first()

    # Return 404 if unknown route
    if not route:
        return redirect(url_for('abort_404')), 307

    # Rename route
    if request.method == 'POST' and request.form.get('set_name'):
        routes_handler.rename(route, request.form['set_name'])

    # Get callbacks
    callbacks = callback_handler.get_callbacks(
        route.id, cursor=request.args.get('cursor'))

    return render_template(
        'inspect.html',
        route_path=route_path,
        callbacks=callbacks,
        cursor=callback_handler.get_cursor(callbacks),
        host_url=request.host_url,
        host_name=urlparse(request.host_url).netloc,
        name=route.name or '',
        name_default='Route created on %s' % (
            (route.creation_date.replace(tzinfo=timezone.utc).astimezone(tz=None)).strftime("%A %B %d, %Y at %I:%M:%S %p")),
    )


@app.route('/api/inspect/<string:route_path>', methods=['GET'])
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

    # Augment callbacks
    for callback in callbacks:
        callback['routes'] = {
            'delete': request.host_url + 'api/delete/' + route_path + '/' + str(callback['id'])
        }

    return jsonify({
        'routes': {
            'inspect': {
                'html': request.host_url + 'inspect/' + route_path,
                'api': request.host_url + 'api/inspect/' + route_path
            },
            'delete': {
                'api': request.host_url + 'api/delete/' + route_path
            },
            'webhook': request.host_url + route_path
        },
        'callbacks': callbacks,
        'creation_date': route.creation_date,
        'expiration_date': route.expiration_date,
        'name': route.name,
        'next': request.host_url + 'api/inspect/' + route_path + '?cursor=' + str(cursor) if cursor else None
    })


@app.route("/api/delete/<string:route_path>/<int:callback_id>")
def delete_callback_json(route_path, callback_id):
    # Lookup route
    route = RouteModel.query.filter_by(path=route_path).first()

    # Return 404 if unknown route
    if not route:
        return jsonify({
            'message': "Invalid route"
        }), 404

    # Delete a callback
    delete = callback_handler.delete(route_id=route.id, id_=callback_id)

    if delete:
        return jsonify({
            'message': "The webhook has been deleted"
        })
    else:
        return jsonify({
            'message': "Invalid route or callback ID"
        }), 400


@app.route('/<string:route_path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def callback(route_path):
    # Lookup route
    route = RouteModel.query.filter_by(path=route_path).first()

    # Return 404 if unknown route
    if not route:
        return redirect(url_for('abort_404')), 307

    # Save callback
    callback_handler.save(route.id)

    # Eventually cleanup old callbacks
    callback_handler.cleanup_old_callbacks()

    return 'OK'


@app.route("/404")
def abort_404():
    return render_template('404.html', host_name=urlparse(request.host_url).netloc), 404
