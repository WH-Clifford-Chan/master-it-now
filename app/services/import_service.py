from app.models import db
from app.models.sets import Card

def get_form_cards(form_data, set_id):
    cards = []
    index = 1

    while True:
        term = (form_data.get(f"term_{index}") or "")
        definition = (form_data.get(f"definition_{index}") or "")
        example = (form_data.get(f"example_{index}") or "")
        notes = (form_data.get(f"notes_{index}") or "")

        # stop condition: no more rows at all
        if not term and not definition and not example and not notes:
            break

        # skip incomplete rows 
        if not term or not definition:
            index += 1
            continue

        cards.append(Card(
            term=term,
            definition=definition,
            example=example,
            notes=notes,
            score=0,
            set_id=set_id
        ))

        index += 1

    db.session.add_all(cards)
    db.session.commit()

