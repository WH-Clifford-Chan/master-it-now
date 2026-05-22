from app.models import db
from datetime import datetime

"""class Course(db.Model):
    __tablename__ = "courses"

    course_id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(120), nullable=False)

    creation_date = db.Column(db.Date, default=datetime.now())

    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    lessons = db.relationship(
    "Lesson",
    backref="course",
    lazy=True,
    cascade="all, delete-orphan")


class Lesson(db.Model):
    __tablename__ = "lesson"

    lesson_id = db.Column(db.Integer, primary_key=True)
    lesson_name = db.Column(db.String(120), nullable=False)
    lesson_content = db.Column(db.Text, nullable=False)
    lesson_quiz = db.Column(db.Text, nullable=True)

    course_id = db.Column(db.Integer, db.ForeignKey("courses.course_id"), nullable=False)"""