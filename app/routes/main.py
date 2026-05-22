from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.models import db
from app.models.sets import Set

main_bp = Blueprint("main", __name__)

@main_bp.route("/dashboard")
@login_required
def dashboard():
    sets = Set.query.filter_by(user_id=current_user.user_id).all()
    return render_template("dashboard.html", user=current_user.username, sets=sets)

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
    return render_template("import.html")

"""
@main_bp.route("/ai_courses")
@login_required
def ai_courses():
    return render_template("ai_lesson.html")

@main_bp.route("/ai_upload")
@login_required
def ai_upload():
    return render_template("ai_upload.html")"""
