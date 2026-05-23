from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from app.models import db
from app.models.sets import Set, Term
from app.models.quiz_session import QuizSession
from app.services.quiz_service import update_term


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
        quiz_session = QuizSession(
            user_id=current_user.user_id,
            set_id=set_id,
            index=0,
            correct=0,
            incorrect=0,
            retype=False,
            feedback="",
            status="active"
        )
        db.session.add(quiz_session)
        db.session.commit()

    vocab_set = Set.query.filter_by(
        set_id=set_id,
        user_id=current_user.user_id
    ).first()

    if not vocab_set:
        flash("Set not found.")
        return redirect(url_for("main.dashboard"))

    terms = Term.query.filter_by(set_id=set_id)\
    .order_by(Term.due_date.asc())\
    .all()

    if not terms:
        flash("No terms found in this set.")
        return redirect(url_for("main.dashboard"))

    if quiz_session.index >= len(terms):
        return redirect(url_for("quiz.summary", set_id=set_id))

    current_term = terms[quiz_session.index]

    correct_answer = (
        current_term.term if mode == "reverse"
        else current_term.definition
    )

    if request.method == "POST":
        answer = request.form.get("answer", "").strip()

        if quiz_session.retype:
            if answer.lower() == correct_answer.lower():
                quiz_session.retype = False
                quiz_session.index += 1
                quiz_session.is_correct = True
                quiz_session.feedback = "Correct. Moving on."
            else:
                quiz_session.feedback = f"Must match the exact answer: {correct_answer}"

            db.session.commit()
            return redirect(url_for("quiz.quiz", set_id=set_id, mode=mode))

        if answer.lower() == correct_answer.lower():
            quiz_session.correct += 1
            quiz_session.index += 1
            quiz_session.is_correct = True
            quiz_session.feedback = "Correct!"
            update_term(current_term.term_id, True)
        else:
            quiz_session.incorrect += 1
            quiz_session.retype = True
            quiz_session.is_correct = False
            quiz_session.feedback = f"Wrong. Correct answer: {correct_answer}"
            update_term(current_term.term_id, False)

        db.session.commit()
        return redirect(url_for("quiz.quiz", set_id=set_id, mode=mode))

    return render_template(
        "quiz.html",
        term=current_term.term if mode == "normal" else current_term.definition,
        total_words=len(terms),
        current_word=quiz_session.index + 1,
        session=quiz_session,
        feedback=quiz_session.feedback,
        retype=quiz_session.retype,
        mode=mode,
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
        db.session.commit()

    return redirect(url_for("main.dashboard"))

@quiz_bp.route("/summary/<int:set_id>", methods=["GET"])
@login_required
def summary(set_id):
    quiz_session = QuizSession.query.filter_by(
        user_id=current_user.user_id,
        set_id=set_id,
        status="active"
    ).first()

    correct = quiz_session.correct if quiz_session else 0
    incorrect = quiz_session.incorrect if quiz_session else 0
    reviewed = quiz_session.index if quiz_session else 0

    return render_template(
        "summary.html",
        correct=correct,
        incorrect=incorrect,
        reviewed=reviewed,
        set_id=set_id
    )
