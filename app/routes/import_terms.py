from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from app.models import db
from app.models.sets import Set, Card
from app.services.import_service import get_form_cards, read_pdf, get_ai_cards, generate_card


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

        get_form_cards(request.form, new_set.set_id)

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
        Card.query.filter_by(set_id=set_id).delete()
        db.session.flush()

        get_form_cards(request.form, set_id)
        db.session.commit()

        return redirect(url_for("main.dashboard"))

    return render_template(
        "import.html",
        editing_set=editing_set
    )

@import_bp.route("/ai_import_pdf", methods=["POST"])
@login_required
def ai_import_pdf():
    pdf = request.files.get("pdf")

    if not pdf:
        return jsonify({
            "error": "No PDF uploaded"
        }), 400

    try:
        # Reset file pointer before reading, just in case
        pdf.seek(0)
        
        # Safe extraction from file stream
        chunks = read_pdf(pdf)
        
        if not chunks:
            return jsonify({
                "error": "Could not extract text from this PDF. Is it scanned or empty?"
            }), 400

        # Structured API call to Gemini
        cards = get_ai_cards(chunks)

        if not cards:
            return jsonify({
                "error": "No flashcards could be generated. Please try a different document structure."
            }), 422

        return jsonify(cards)

    except Exception as e:
        return jsonify({
            "error": "Failed to process PDF",
            "details": str(e)
        }), 500
    
@import_bp.route("/ai_generate_card", methods=["GET", "POST"])
@login_required
def ai_generate_card():
    if request.method == "POST":
        term = request.json.get("term")
        card = generate_card(term)
        return jsonify(card)

@import_bp.route("/ai_import", methods=["GET", "POST"])
@login_required
def ai_import():
    error = None
    if request.method == "POST":
        set_name = request.form.get("set_name")

        if not set_name:
            error = "Set name and terms are required."
            return render_template("ai_import.html", error=error)

        new_set = Set(
            set_name=set_name,
            user_id=current_user.user_id
        )

        db.session.add(new_set)
        db.session.commit()

        get_form_cards(request.form, new_set.set_id)

        return redirect(url_for('main.dashboard'))

    return render_template("ai_import.html", error=error)
















