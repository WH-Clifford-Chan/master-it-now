from flask import Blueprint, redirect, url_for, request, jsonify, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app.models import db
from app.models.sets import Set, Card
from app.services.import_service import get_form_cards, read_pdf, get_ai_cards, generate_card
import os
from app.utils import render_platform_template

import_bp = Blueprint("import", __name__)


def _save_uploaded_image(image_file):
    if not image_file or not getattr(image_file, "filename", None):
        return None

    uploads_dir = os.path.abspath(os.path.join(current_app.root_path, "..", "uploads"))
    os.makedirs(uploads_dir, exist_ok=True)

    filename = secure_filename(image_file.filename)
    save_path = os.path.join(uploads_dir, filename)
    base, ext = os.path.splitext(filename)
    counter = 1

    while os.path.exists(save_path):
        filename = f"{base}_{counter}{ext}"
        save_path = os.path.join(uploads_dir, filename)
        counter += 1

    image_file.save(save_path)
    return filename


def _delete_saved_image(filename):
    if not filename:
        return

    uploads_dir = os.path.abspath(os.path.join(current_app.root_path, "..", "uploads"))
    save_path = os.path.join(uploads_dir, filename)
    if os.path.exists(save_path):
        os.remove(save_path)

@import_bp.route("/form_import", methods=["GET", "POST"])
@login_required
def form_import():
    error = None
    if request.method == "POST":
        set_name = request.form.get("set_name")

        if not set_name:
            error = "Set name and terms are required."
            return render_platform_template("ai_import.html", error=error)

        new_set = Set(
            set_name=set_name,
            user_id=current_user.user_id
        )

        db.session.add(new_set)
        db.session.commit()

        get_form_cards(request, new_set.set_id)
        db.session.commit()

        return redirect(url_for('main.flashcard_sets'))

    return render_platform_template("ai_import.html", error=error)

@import_bp.route("/edit_set/<int:set_id>", methods=["GET", "POST"])
@login_required
def edit_set(set_id):
    editing_set = Set.query.filter_by(set_id=set_id).first_or_404()

    if request.method == "POST":

        set_name = request.form.get("set_name")

        if not set_name:
            return render_platform_template(
                "ai_import.html",
                error="Set name is required.",
                editing_set=editing_set
            )

        editing_set.set_name = set_name

        submitted_rows = []
        index = 1
        while True:
            card_id = (request.form.get(f"card_id_{index}") or "").strip()
            term = (request.form.get(f"term_{index}") or "").strip()
            definition = (request.form.get(f"definition_{index}") or "").strip()
            example = (request.form.get(f"example_{index}") or "").strip()
            notes = (request.form.get(f"notes_{index}") or "").strip()
            
            if not term and not definition and not example and not notes and not card_id:
                break

            if not term or not definition:
                index += 1
                continue

            submitted_rows.append({
                "card_id": card_id,
                "term": term,
                "definition": definition,
                "example": example,
                "notes": notes,
                "index": index
            })
            index += 1

        existing = {c.card_id: c for c in Card.query.filter_by(set_id=set_id).all()}
        seen = set()

        for row in submitted_rows:
            card_id = row["card_id"]

            if card_id:
                card = existing.get(int(card_id))
                if card is None:
                    continue
                seen.add(card.card_id)
            else:
                card = Card(set_id=set_id)
                db.session.add(card)

            card.term = row["term"]
            card.definition = row["definition"]
            card.example = row["example"]
            card.notes = row["notes"]

            # Handle uploaded front image for this row (if any)
            delete_image = request.form.get(f"delete_image_{row['index']}") == "1"
            image_file = request.files.get(f"image_front_{row['index']}")
            saved_name = _save_uploaded_image(image_file)

            if delete_image:
                _delete_saved_image(card.front_image)
                card.front_image = ""
            elif saved_name:
                card.front_image = saved_name

        for card_id, card in existing.items():
            if card_id not in seen:
                db.session.delete(card)

        db.session.commit()

        return redirect(url_for("main.flashcard_sets"))

    return render_platform_template(
        "ai_import.html",
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
            return render_platform_template("ai_import.html", error=error)

        new_set = Set(
            set_name=set_name,
            user_id=current_user.user_id
        )

        db.session.add(new_set)
        db.session.commit()

        get_form_cards(request, new_set.set_id)
        db.session.commit()

        return redirect(url_for('main.flashcard_sets'))

    return render_platform_template("ai_import.html", error=error)
















