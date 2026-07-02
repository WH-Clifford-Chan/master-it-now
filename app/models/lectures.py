from app.models import db
from datetime import date

class Lecture(db.Model):
    __tablename__ = "lectures"

    lecture_id = db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(db.Date, nullable=False, default=date.today)

    lecture_summary = db.Column(db.Text, nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)

    lecture_quiz = db.Column(db.JSON, nullable=True)
    
