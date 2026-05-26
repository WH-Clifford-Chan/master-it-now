from datetime import date, timedelta
from app.models import db
from app.models.sets import Card
import random

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
        card.interval = 1
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
        else:
            card.interval = round(card.interval * card.ef)

    card.due_date = (
        date.today()
        + timedelta(days=int(card.interval * random.uniform(0.9, 1.1)))
    )
    card.last_learned = date.today()

    db.session.commit()

