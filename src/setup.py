from .models import db


def setup():
    # Create models
    db.create_all()

    print('Setup complete.')

    return True


if __name__ == '__main__':
    setup()
