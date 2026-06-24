from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from flask_babel import gettext as _
from app.models import db
from app.models.sets import Set, Card
from app.models.sessions import QuizSession
from app.services.quiz_service import check_similarity, normalize
import random


quiz_bp = Blueprint("quiz", __name__)

@quiz_bp.route("/quiz/<int:set_id>", methods=["GET", "POST"])
@login_required
def quiz(set_id):
    mode = request.args.get("mode", "normal")

    quiz_session = QuizSession.query.filter_by(
        user_id=current_user.user_id,
        set_id=set_id,
        status="active"
    ).first()

    if not quiz_session:
        terms = (
            Card.query.filter_by(set_id=set_id)
            .order_by(Card.due_date.asc())
            .all()
        )

        random.shuffle(terms)

        quiz_session = QuizSession(
            user_id=current_user.user_id,
            set_id=set_id,
            index=0,
            correct=0,
            incorrect=0,
            retype=False,
            feedback="",
            status="active",
            term_order=[t.card_id for t in terms]  # lock order
        )

        db.session.add(quiz_session)
        db.session.commit()

    vocab_set = Set.query.filter_by(
        set_id=set_id,
        user_id=current_user.user_id
    ).first()

    if not vocab_set:
        flash("Set not found.")
        return redirect(url_for("main.quizzes"))

    if not quiz_session.term_order:
        flash("Quiz session corrupted.")
        return redirect(url_for("main.quizzes"))
    
    term_order = quiz_session.term_order

    if not term_order:
        flash("Quiz session corrupted.")
        return redirect(url_for("main.quizzes"))

    if quiz_session.index >= len(term_order):
        quiz_session.status = "completed"
        db.session.commit()
        return redirect(url_for("quiz.summary", set_id=set_id))

    current_term = Card.query.get(term_order[quiz_session.index])

    correct_answer = (
        current_term.term if mode == "reverse"
        else current_term.definition
    )

    if request.method == "POST":
        answer = request.form.get("answer", "").strip()

        if quiz_session.retype:
            if normalize(answer) == normalize(correct_answer):
                quiz_session.retype = False
                quiz_session.index += 1
                quiz_session.is_correct = True
                quiz_session.feedback_key = "retry_correct"
            else:
                quiz_session.feedback_key = "retry"

            db.session.commit()
            return redirect(url_for("quiz.quiz", set_id=set_id, mode=mode))
        
        is_correct = check_similarity(correct_answer, answer)
        if is_correct:
            quiz_session.correct += 1
            quiz_session.index += 1
            quiz_session.is_correct = True
            feedback = _("Correct!")
            quiz_session.feedback_key = "correct"
        else:
            quiz_session.incorrect += 1
            quiz_session.retype = True
            quiz_session.is_correct = False
            quiz_session.feedback_key = "wrong"

        db.session.commit()
        return redirect(url_for("quiz.quiz", set_id=set_id, mode=mode))

    return render_template(
        "quiz.html",
        term=current_term.term if mode == "normal" else current_term.definition,
        total_words=len(quiz_session.term_order),
        current_word=quiz_session.index + 1,
        session=quiz_session,
        feedback_key=quiz_session.feedback_key,
        retype=quiz_session.retype,
        mode=mode,
        correct_answer=correct_answer,
        correct=quiz_session.is_correct
    )

@quiz_bp.route("/quiz/<int:set_id>/reset", methods=["POST"])
@login_required
def reset_quiz(set_id):
    quiz_session = QuizSession.query.filter_by(
        user_id=current_user.user_id,
        set_id=set_id,
        status="active"
    ).first()

    if quiz_session:
        quiz_session.index = 0
        quiz_session.correct = 0
        quiz_session.incorrect = 0
        quiz_session.retype = False
        quiz_session.feedback = ""
        quiz_session.status = "active"
        db.session.commit()

    return redirect(url_for("main.quizzes"))

@quiz_bp.route("/summary/<int:set_id>", methods=["GET", "POST"])
@login_required
def summary(set_id):

    quiz_session = (
        QuizSession.query.filter_by(
            user_id=current_user.user_id,
            set_id=set_id
        )
        .order_by(QuizSession.session_id.desc())
        .first()
    )

    if not quiz_session:
        flash("No quiz session found.")
        return redirect(url_for("main.quizzes"))

    correct = quiz_session.correct
    incorrect = quiz_session.incorrect
    reviewed = len(quiz_session.term_order or [])

    return render_template(
        "summary.html",
        correct=correct,
        incorrect=incorrect,
        reviewed=reviewed,
        set_id=set_id
    )
