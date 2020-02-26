import uuid
from datetime import datetime

from .models import db, RouteModel, CallbackModel


def new():
    """ Create a new route """

    # Create route
    route = RouteModel(path=str(uuid.uuid4()))
    db.session.add(route)
    db.session.commit()

    return route


def rename(route, name):
    """ Rename a route """

    if not name:
        return None

    # Rename the route
    route.name = name

    # Commit
    db.session.commit()


def cleanup_old_routes():
    """ Delete expired routes """

    # Load routes
    routes = RouteModel.query.filter(
        RouteModel.expiration_date < datetime.utcnow(), RouteModel.expiration_date.isnot(None)).all()

    for route in routes:
        delete(route)


def delete(route):
    """ Delete a route and all its callbacks """

    # Delete callbacks
    CallbackModel.query.filter_by(route_id=route.id).delete()

    # Delete route
    db.session.delete(route)

    # Commit
    db.session.commit()
