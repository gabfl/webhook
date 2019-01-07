import uuid
from dateparser import parse

from .models import db, RouteModel, CallbackModel


def new():
    """ Create a new route """

    # Create route
    route = RouteModel(path=str(uuid.uuid4()))
    db.session.add(route)
    db.session.commit()

    return route


def cleanup_old_routes():
    """ Delete old routes """

    # Deletion date limit
    date_limit = parse('1 week ago')

    # Load routes
    routes = RouteModel.query.filter(
        RouteModel.creation_date < date_limit).all()

    for route in routes:
        # Delete callbacks
        CallbackModel.query.filter_by(route_id=route.id).delete()

        # Delete route
        db.session.delete(route)

        # Commit
        db.session.commit()
