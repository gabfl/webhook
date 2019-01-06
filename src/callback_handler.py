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


def is_json(data):
    """ Validate if a string is a Json """

    try:
        json.loads(data)

        return True
    except Exception:
        return False
