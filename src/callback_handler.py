import json

from flask import request

from .bootstrap import get_or_create_app
from .models import db, CallbackModel


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


def get_callbacks(route_id):
    """ Prepare and returns the callbacks for a route ID """

    # Load callbacks
    callbacks = CallbackModel.query.filter_by(
        route_id=route_id).order_by(CallbackModel.id.desc()).all()

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


def is_json(data):
    """ Validate if a string is a Json """

    try:
        json.loads(data)

        return True
    except Exception:
        return False
