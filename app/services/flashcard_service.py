from datetime import date, timedelta
from app.models import db
from app.models.sets import Card
import random
from sqlalchemy.sql import func

def next_card(set_id, current_card):
    groups = [
        (
            Card.query.filter_by(set_id=set_id, queue="never")
            .order_by(Card.due_date.asc())
            .first(),
            0.5,
        ),
        (
            Card.query.filter_by(set_id=set_id, queue="learning")
            .order_by(Card.due_date.asc())
            .first(),
            0.4,
        ),
        (
            Card.query.filter_by(set_id=set_id, queue="mastered")
            .order_by(Card.due_date.asc())
            .first(),
            0.025,
        ),
        (
            Card.query.filter_by(set_id=set_id, queue="learning") \
            .order_by(func.random()) \
            .first(),
            0.075
        )
    ]

    available_cards = [card for card, _ in groups if card]
    available_weights = [weight for card, weight in groups if card]

    if not available_cards:
        return None

    card = random.choices(
        available_cards,
        weights=available_weights,
        k=1
    )[0]

    if card != current_card:
        return card

    # Fallback if we picked the current card
    alternatives = [c for c in available_cards if c != current_card]

    return random.choice(alternatives) if alternatives else card

def update_card(card_id, rating):
    card = Card.query.filter_by(
        card_id=card_id
    ).first()

    quality = 2.5

    if rating == "forgot":
        quality = 0
    elif rating == "hard":
        quality = 1
    elif rating == "good":
        quality = 3
    elif rating == "easy":
        quality = 5

    if not card:
        return
    
    q = max(0, min(5, quality))
    if q < 3:
        card.repetitions = 0 
        card.interval = 0
        if rating == "forgot":
            card.due_date = date.today()
            card.queue == "never"
    else:
        ef = card.ef
        ef += (
            0.1
            - (5 - quality)
            * (0.08 + (5 - quality) * 0.02)
        )
        card.ef = max(1.3, ef)

        card.repetitions += 1

        if card.repetitions == 1:
            card.interval = 1
        elif card.repetitions == 2:
            card.interval = 6
            card.queue == "learning"
        else:
            card.interval = round(card.interval * card.ef)
            if card.repetitions >= 5 and q == 5:
                card.queue == "mastered"

    card.due_date = (
        date.today()
        + timedelta(days=int(card.interval * random.uniform(0.9, 1.1)))
    )
    card.last_learned = date.today()

    db.session.commit()

