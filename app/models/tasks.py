from app.models import db

class Task(db.Model):
    __tablename__ = "tasks"

    task_id = db.Column(
        db.Integer,
        primary_key=True
    )

    to_do_morning = db.Column(
        db.JSON,
        nullable=False,
        default=list
    )

    to_do_afternoon = db.Column(
        db.JSON,
        nullable=False,
        default=list
    )

    to_do_evening = db.Column(
        db.JSON,
        nullable=False,
        default=list
    )

    in_progress = db.Column(
        db.JSON,
        nullable=False,
        default=list
    )

    completed = db.Column(
        db.JSON,
        nullable=False,
        default=list
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False,
        unique=True
    )

