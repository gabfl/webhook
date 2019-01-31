from .models import db

# Create models
db.create_all()

print('Setup complete.')
