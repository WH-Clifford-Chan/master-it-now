from app.models import db
from datetime import date

class Set(db.Model):
    __tablename__ = "sets"

    set_id = db.Column(db.Integer, primary_key=True)
    set_name = db.Column(db.String(120), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    terms = db.relationship("Term", backref="set", lazy=True, cascade="all, delete-orphan")

class Term(db.Model):
    __tablename__ = "terms"

    term_id = db.Column(db.Integer, primary_key=True)
    
    term = db.Column(db.String(80), nullable=False)
    definition = db.Column(db.String(120), nullable=False)

    score = db.Column(db.Integer, nullable=False)
    last_learned = db.Column(db.Date, default=date.today)

    set_id = db.Column(db.Integer, db.ForeignKey("sets.set_id"), nullable=False)