from app.models import db
from datetime import date, datetime

class Set(db.Model):
    __tablename__ = "sets"

    set_id = db.Column(db.Integer, primary_key=True)
    set_name = db.Column(db.String(120), nullable=False)
    last_opened = db.Column(db.DateTime, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    cards = db.relationship("Card", backref="set", lazy=True, cascade="all, delete-orphan")

class Card(db.Model):
    __tablename__ = "cards"
    card_id = db.Column(db.Integer, primary_key=True)

    # Core
    term = db.Column(db.String(100), nullable=False)
    definition = db.Column(db.String(255), nullable=False)
     
    # Optional for cards
    example = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.String(255), nullable=True)

    # Spaced repetition
    ef = db.Column(db.Float, nullable=False, default=2.5) # easiness_factor
    interval = db.Column(db.Integer, default=0)
    repetitions = db.Column(db.Integer, default=0)
    last_learned = db.Column(db.Date, default=date.today)
    due_date = db.Column(db.Date, nullable=False, default=date.today)
    queue = db.Column(db.String(20), nullable=False, default="never")

    # Quiz score
    score = db.Column(db.Integer, default=0)

    set_id = db.Column(db.Integer, db.ForeignKey("sets.set_id"), nullable=False)




# Old Term model
""" class Term(db.Model):
    __tablename__ = "terms"
    
    term_id = db.Column(db.Integer, primary_key=True)
    
    # Core
    term = db.Column(db.String(100), nullable=False)
    definition = db.Column(db.String(255), nullable=False)

    set_id = db.Column(db.Integer, db.ForeignKey("sets.set_id"), nullable=False)
"""

# Use for later
"""
class CardMedia(db.Model):
    __tablename__ = "card_media"
    media_id = db.Column(db.Integer, primary_key=True)

    card_id = db.Column(
        db.Integer,
        db.ForeignKey("cards.card_id")
    )

    media_type = db.Column(db.String(20))
    field_name = db.Column(db.String(50))

    file_path = db.Column(db.String(255))"""