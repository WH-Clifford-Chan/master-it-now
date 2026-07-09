from flask_sqlalchemy import SQLAlchemy
import sqlite3
import os

# create the db object here
db = SQLAlchemy()

# Import model modules so SQLAlchemy metadata includes all tables.
from app.models import sessions, user, sets, ai_courses, tasks # Not used yet: , lectures


def init_db(app):
    db.init_app(app)

    with app.app_context():
        db.create_all()



