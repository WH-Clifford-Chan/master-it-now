from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import current_user, login_required
from app.models import db
from app.models.sets import Set, Term
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

@import_bp.route("/edit_set/<int:set_id>", methods=["GET", "POST"])
@login_required
def edit_set(set_id):
    editing_set = Set.query.filter_by(set_id=set_id).first_or_404()

    if request.method == "POST":

        set_name = request.form.get("set_name")

        if not set_name:
            return render_template(
                "import.html",
                error="Set name is required.",
                editing_set=editing_set
            )

        editing_set.set_name = set_name
        Term.query.filter_by(set_id=set_id).delete()

        db.session.commit()

        get_form_terms(request.form, set_id)

        return redirect(url_for("main.dashboard"))

    return render_template(
        "import.html",
        editing_set=editing_set
    )

















