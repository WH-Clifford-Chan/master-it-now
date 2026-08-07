from flask import Blueprint, request, redirect, url_for
from flask_login import login_required, current_user
from app.models import db
from app.models.sets import Set
from app.models.lectures import Lecture
from app.utils import render_platform_template

main_bp = Blueprint("main", __name__)

@main_bp.route("/quizzes")
@login_required
def quizzes():
    sets = Set.query.filter_by(user_id=current_user.user_id).all()
    set_lengths = {
        s.set_id: len(s.cards) for s in sets
    }
    return render_platform_template(
        "quizzes.html", 
        user=current_user.username, 
        sets=sets,
        set_lengths=set_lengths)

@main_bp.route("/flashcard_sets")
@login_required
def flashcard_sets():
    sets = Set.query.filter_by(user_id=current_user.user_id).all()

    recents = (Set.query
    .filter_by(user_id=current_user.user_id)
    .order_by(Set.last_opened.desc())
    .limit(3)
    .all() )

    set_lengths = {
        s.set_id: len(s.cards) for s in sets
    }

    recent_lengths = {
        r.set_id: len(r.cards) for r in recents
    }

    return render_platform_template(
        "flashcard_sets.html", 
        user=current_user.username, 
        sets=sets,
        recents=recents,
        set_lengths=set_lengths)

@main_bp.route("/plans")
@login_required
def plans():
    return render_platform_template("paid_plans.html")

@main_bp.route("/lectures")
@login_required
def lectures():
    lectures = Lecture.query.filter_by(user_id=current_user.user_id).all()
    dates = {
        lecture.lecture_id: lecture.creation_date for lecture in lectures
    }
    return render_platform_template(
        "lectures.html",
        user=current_user.username,
        lectures=lectures,
        dates=dates)
    

@main_bp.route("/sets/rename/<int:set_id>", methods=["POST"])
@login_required
def rename_set(set_id):
    data = request.get_json()
    new_name = (data.get("name") or "").strip()

    if not new_name:
        return {"error": "Invalid name"}, 400

    set_obj = db.session.get(Set, set_id)

    if not set_obj or set_obj.user_id != current_user.user_id:
        return {"error": "Set not found"}, 404

    set_obj.set_name = new_name

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

    return {"success": True}, 200

@main_bp.route("/sets/delete/<int:set_id>", methods=["POST"])
@login_required
def delete_set(set_id):
    set_obj = db.session.get(Set, set_id)

    if not set_obj or set_obj.user_id != current_user.user_id:
        return {"error": "Set not found"}, 404

    try:
        db.session.delete(set_obj)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

    return {"success": True}, 200


@main_bp.route("/upload")
@login_required
def upload():
    return render_platform_template("import.html")


