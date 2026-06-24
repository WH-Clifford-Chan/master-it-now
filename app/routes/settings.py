from flask import Blueprint, render_template, request, session
from flask_login import login_required, current_user

settings_bp = Blueprint("settings", __name__)

@settings_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    return render_template(
        "settings.html",
        user=current_user.username,
        password_updated=request.args.get("password_updated"),
        username_updated=request.args.get("username_updated"),
        error=request.args.get("error"),
        LANGUAGE=session.get("lang", "en")
    )

