from app.models import db

class QuizSession(db.Model):
    __tablename__ = "quiz_sessions"

    session_id = db.Column(db.Integer, primary_key=True)
    index = db.Column(db.Integer, nullable=False, default=0)
    term_order = db.Column(db.PickleType, nullable=True)

    correct = db.Column(db.Integer, nullable=False, default=0)
    incorrect = db.Column(db.Integer, nullable=False, default=0)
    retype = db.Column(db.Boolean, nullable=False, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    set_id = db.Column(db.Integer, db.ForeignKey("sets.set_id"), nullable=False)

    status = db.Column(db.String(20), default="active")
    feedback = db.Column(db.String(255), default="")
    feedback_key = db.Column(db.String(50), nullable=True)
    is_correct = db.Column(db.Boolean, nullable=True)


 
