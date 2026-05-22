from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import current_user, login_required
from app.models import db
from app.models.sets import Set
from app.services.import_service import get_form_terms

import_bp = Blueprint("import", __name__)

@import_bp.route("/form_import", methods=["GET", "POST"])
@login_required
def form_import():
    error = None
    if request.method == "POST":
        set_name = request.form.get("set_name")

        if not set_name:
            error = "Set name and terms are required."
            return render_template("import.html", error=error)

        new_set = Set(
            set_name=set_name,
            user_id=current_user.user_id
        )

        db.session.add(new_set)
        db.session.commit()

        get_form_terms(request.form, new_set.set_id)

        return redirect(url_for('main.dashboard'))

    return render_template("import.html", error=error)



















""" @import_bp.route("/file_import")
@login_required
def file_import():
    return render_template("import.html")

@import_bp.route("/ai_import")
@login_required
def ai_import():
    return render_template("import.html") """