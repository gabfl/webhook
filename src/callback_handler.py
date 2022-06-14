import json

from flask import request
from dateparser import parse

from .bootstrap import get_or_create_app
from .models import db, CallbackModel
from .config import Config


app = get_or_create_app()


def get_headers():
    """ Retrieve all headers """

    headers = {}

    for header_name, header_value in request.headers:
        headers[header_name] = header_value

    return headers


def save(route_id):
    """ Save callback """

    # Optionally dump Json
    body = request.get_data().decode('utf-8')
    if is_json(body):
        body = json.dumps(request.get_json())

    # Save callback
    callback = CallbackModel(
        route_id=route_id,
        headers=json.dumps(get_headers()),
        method=request.method,
        args=json.dumps(request.args) if request.args else None,
        body=body,
        referrer=request.referrer,
        remote_addr=request.remote_addr
    )

    db.session.add(callback)
    db.session.commit()

    return True


def cleanup_old_callbacks():
    """ Delete expired callbacks """

    # Get desired expiration
    delete_callback_older_than = Config().delete_callback_older_than

    if not delete_callback_older_than:
        return None

    # Parse expiration date
    dt = parse(delete_callback_older_than, settings={'TIMEZONE': 'UTC'})

    # Load callbacks (limit 50 to avoid slow HTTP responses)
    callbacks = CallbackModel.query.filter(
        CallbackModel.date < dt).limit(50).all()

    for callback in callbacks:
        # Delete callback
        db.session.delete(callback)

    # Commit
    db.session.commit()


def delete(route_id, id_):
    """ Delete a callback """

    # Lookup callback
    callback = CallbackModel.query.filter_by(
        route_id=route_id).filter_by(id=id_).first()

    if callback:
        # Delete callback
        db.session.delete(callback)

        # Commit
        db.session.commit()

        return True

    return False


def get_callbacks(route_id, cursor=None, limit=50):
    """ Prepare and returns the callbacks for a route ID """

    # Load callbacks
    callbacks = CallbackModel.query.filter_by(route_id=route_id)
    if cursor:
        callbacks = callbacks.filter(CallbackModel.id < cursor)
    callbacks = callbacks.order_by(CallbackModel.id.desc()).limit(limit).all()

    # Process rows
    callbacks_processed = []
    for callback in callbacks:
        # Prepare body
        body = {
            'data': callback.body if callback.body else None,
            'size': len(callback.body) if callback.body else 0
        }
        if body['data'] and is_json(body['data']):
            body['data'] = json.loads(body['data'])

        # Prepare args
        args = None
        if callback.args:
            args = json.loads(callback.args)

        callbacks_processed.append(
            {
                'id': callback.id,
                'headers': json.loads(callback.headers),
                'method': callback.method,
                'args': args,
                'body': body,
                'date': callback.date,
                'referrer': callback.referrer,
                'remote_addr': callback.remote_addr
            }
        )

    return callbacks_processed


def get_cursor(callbacks, limit=50):
    """ Returns the next page cursor """

    return callbacks[-1].get('id') if callbacks and len(callbacks) >= limit else None


def is_json(data):
    """ Validate if a string is a Json """

    try:
        json.loads(data)

        return True
    except Exception:
        return False
