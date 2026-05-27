from flask_sqlalchemy import SQLAlchemy

# create the db object here
db = SQLAlchemy()

# Import model modules so SQLAlchemy metadata includes all tables.
from app.models import sessions, user, sets, ai_courses, tasks


def init_db(app):
    db.init_app(app)

    # create tables
    with app.app_context():
        db.create_all()

