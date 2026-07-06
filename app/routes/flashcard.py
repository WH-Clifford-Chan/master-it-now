from flask import Blueprint, redirect, request, session, url_for, flash
from flask_login import login_required, current_user
from app.models.sessions import CardSession
from app.models.sets import Set, Card
from app.models import db
from app.services.flashcard_service import update_card, next_card
from app.utils import render_platform_template
from datetime import datetime

flashcard_bp = Blueprint("flashcard", __name__)

@flashcard_bp.route("/flashcard/<int:set_id>", methods=["GET", "POST"])
@login_required
def flashcard(set_id):

    card_set = Set.query.filter_by(
        set_id=set_id,
        user_id=current_user.user_id
    ).first()

    if not card_set:
        flash("Set not found.")
        return redirect(url_for("main.flashcard_sets"))

    card_session = CardSession.query.filter_by(
        user_id=current_user.user_id,
        set_id=set_id,
        status="active"
    ).first()

    if not card_session:
        card_session = CardSession(
            user_id=current_user.user_id,
            set_id=set_id,
            index=0,
            status="active",
        )
        db.session.add(card_session)
        db.session.commit()

    current_card = None

    if getattr(card_session, "current_card_id", None):
        current_card = Card.query.get(card_session.current_card_id)

    if current_card is None:
        current_card = next_card(set_id, None)

        if not current_card:
            flash("No cards available.")
            return redirect(url_for("main.flashcard_sets"))

        card_session.current_card_id = current_card.card_id
        db.session.commit()

    if request.method == "POST":
        rating = request.form.get("rating")

        update_card(current_card.card_id, rating)

        if rating != "forgot":
            current_card.queue = "learning"

        next_review = next_card(set_id, current_card)

        card_session.index += 1

        if next_review:
            card_session.current_card_id = next_review.card_id
        else:
            card_session.status = "completed"

        db.session.commit()

        return redirect(
            url_for("flashcard.flashcard", set_id=set_id)
        )

    return render_platform_template(
        "flashcard.html",
        set_name=card_set.set_name,
        index=card_session.index + 1,
        session=card_session,
        set_id=set_id,
        card_id=current_card.card_id,
        term=current_card.term,
        definition=current_card.definition,
        example=current_card.example,
        notes=current_card.notes
    )

@flashcard_bp.route("/flashcard/<int:set_id>/<int:card_id>/edit", methods=["POST"])
@login_required
def edit_flashcard(set_id, card_id):
    card = Card.query.filter_by(
        card_id=card_id,
        set_id=set_id
    ).first()

    if not card:
        flash("Card not found.")
        return redirect(url_for("flashcard.flashcard", set_id=set_id))

    card.term = request.form.get("term", card.term)
    card.definition = request.form.get("definition", card.definition)
    card.example = request.form.get("example", card.example)
    card.notes = request.form.get("notes", card.notes)

    db.session.commit()

    return redirect(url_for("flashcard.flashcard", set_id=set_id))

@flashcard_bp.route("/flashcard/<int:set_id>/end", methods=["GET", "POST"])
@login_required
def end_flashcard(set_id):
    card_session = CardSession.query.filter_by(
        user_id=current_user.user_id,
        set_id=set_id,
        status="active"
    ).first()

    current_set = Set.query.filter_by(
        user_id=current_user.user_id, 
        set_id=set_id, 
    ).first()

    if card_session:
        card_session.index = 0
        card_session.status = "inactive"
        current_set.last_opened = datetime.now()
        db.session.commit()

    return redirect(url_for("main.flashcard_sets"))

@flashcard_bp.route("/flashcard_summary/<int:set_id>", methods=["GET"])
@login_required
def flashcard_summary(set_id):
    card_session = (
        CardSession.query.filter_by(
            user_id=current_user.user_id,
            set_id=set_id
        )
        .order_by(CardSession.session_id.desc())
        .first()
    )

    if not card_session:
        flash("No quiz session found.")
        return redirect(url_for("main.flashcard_sets"))

    reviewed = len(card_session.card_order or [])
    
    # Delete Session
    db.session.delete(card_session)
    db.session.commit()

    return render_platform_template(
        "flashcard_summary.html",
        reviewed=reviewed,
        set_id=set_id
    )



