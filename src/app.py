import json

from flask import Flask, render_template, request
from flask import Flask, redirect, url_for

from bootstrap import get_or_create_app
import callback_handler
import routes_handler
from models import db, RouteModel, CallbackModel


app = get_or_create_app()


@app.route("/")
def hp():
    return render_template('index.html')


@app.route("/new")
def new():
    # Cleanup old routes
    routes_handler.cleanup_old_routes()

    # Generate a new route
    new_route = routes_handler.new()

    return redirect('/' + new_route + '/inspect')


@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    # Get route
    route_path = path

    # If we are inspecting a route
    inspect = False
    if route_path.rfind('/inspect') > 0:
        inspect = True
        route_path = route_path.rstrip('/inspect')

    # Lookup route
    route = RouteModel.query.filter_by(route=route_path).first()

    # Return 404 if unknown route
    if not route:
        return redirect(url_for('abort_404'))

    if inspect:
        # Load callbacks
        callbacks = CallbackModel.query.filter_by(
            route_id=route.id).order_by(CallbackModel.date.desc()).all()

        # Process rows
        callbacks_processed = []
        for callback in callbacks:
            # Prepare body
            body = callback.body
            if callback_handler.is_json(body):
                body = json.loads(body)

            callbacks_processed.append(
                {
                    'headers': json.loads(callback.headers),
                    'method': callback.method,
                    'post': callback.post,
                    'args': callback.args,
                    'body': body,
                    # 'body_is_json': callback_handler.is_json(callback.body),
                    'date': callback.date,
                    'referrer': callback.referrer,
                    'remote_addr': callback.remote_addr
                }
            )

        return render_template(
            'inspect.html',
            route_path=route_path,
            callbacks=callbacks_processed,
            host_url=request.host_url
        )
    else:
        # Save callback
        callback_handler.save(route.id)

        return 'OK'


@app.route("/404")
def abort_404():
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.debug = True
    app.run()
