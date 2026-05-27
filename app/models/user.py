from app.models import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    sets = db.relationship("Set", backref="user", lazy=True)
    # courses = db.relationship("Course", backref="user", lazy=True)
    quiz_sessions = db.relationship("QuizSession", backref="user", lazy=True)
    card_sessions = db.relationship("CardSession", backref="user", lazy=True)
    tasks = db.relationship("Task", backref="user", lazy=True)

    def get_id(self):
        return str(self.user_id)