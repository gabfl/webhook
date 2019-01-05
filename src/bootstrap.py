from flask import Flask

app = None


def get_or_create_app():
    """
        Returns Flask app
    """

    global app

    if not app:
        app = Flask(__name__, template_folder='templates/')

    return app
