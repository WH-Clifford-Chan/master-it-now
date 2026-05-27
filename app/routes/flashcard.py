from flask import Blueprint, redirect, request, session, url_for, flash, render_template
from flask_login import login_required, current_user
from app.models.sessions import CardSession
from app.models.sets import Set, Card
from app.models import db
from app.services.flashcard_service import update_card

flashcard_bp = Blueprint("flashcard", __name__)

@flashcard_bp.route("/flashcard/<int:set_id>", methods=["GET", "POST"])
@login_required
def flashcard(set_id):
    card_session = CardSession.query.filter_by(
        user_id=current_user.user_id,
        set_id=set_id,
        status="active"
    ).first()

    if not card_session:
        cards = (
            Card.query.filter_by(set_id=set_id)
            .order_by(Card.due_date.asc())
            .all()
        )

        card_session = CardSession(
            user_id = current_user.user_id,
            set_id=set_id,
            index=0,
            status="active",
            card_order=[card.card_id for card in cards] # lock order
        )

        db.session.add(card_session)
        db.session.commit()

        card_set = Set.query.filter_by(
        set_id=set_id,
        user_id=current_user.user_id
        ).first()

        if not card_set:
            flash("Set not found.")
            return redirect(url_for("main.flashcard_sets"))

        if not card_session.card_order:
            flash("Card session corrupted.")
            return redirect(url_for("main.flashcard_sets"))
        
    if not card_session.card_order or len(card_session.card_order) == 0:
        flash("No cards available in this session.")
        return redirect(url_for("main.flashcard_sets"))
        
    if card_session.index >= len(card_session.card_order):
        card_session.status = "completed"
        db.session.commit()
        return redirect(url_for("flashcard.flashcard_summary", set_id=set_id))
        
    current_card = Card.query.get(card_session.card_order[card_session.index])

    if request.method == "POST":
        rating = request.form.get("rating")

        # Show forgotten card after 5 cards
        if rating == "forgot":
            current_index = card_session.index
            card_order = card_session.card_order.copy()  # work on a copy
            forgot_card = card_order.pop(current_index)
            new_index = min(current_index + 5, len(card_order))
            card_order.insert(new_index, forgot_card)
            card_session.card_order = card_order          # assign the new list
        else:
            card_session.index += 1

        update_card(current_card.card_id, rating)
        db.session.commit()
        return redirect(url_for("flashcard.flashcard", set_id=set_id))
    
    return render_template(
        "flashcard.html",
        index=card_session.index + 1,
        session=card_session,
        term=current_card.term,
        definition=current_card.definition,
        example=current_card.example,
        notes=current_card.notes
    )

@flashcard_bp.route("/flashcard/<int:set_id>/reset", methods=["POST"])
@login_required
def reset_flashcard(set_id):
    card_session = CardSession.query.filter_by(
        user_id=current_user.user_id,
        set_id=set_id,
        status="active"
    ).first()

    if card_session:
        card_session.index = 0
        card_session.status = "active"
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

    return render_template(
        "flashcard_summary.html",
        reviewed=reviewed,
        set_id=set_id
    )



