from app.models import db
from app.models.sets import Term

def get_form_terms(form_data, set_id):
    terms = []
    index = 1
    max_limit = 200  # safety guard

    for index in range(1, max_limit):
        term = form_data.get(f"term_{index}")
        definition = form_data.get(f"definition_{index}")

        if term is None and definition is None:
            continue

        if not term or not definition:
            continue

        terms.append(Term(
            term=term,
            definition=definition,
            score=0,
            set_id=set_id
        ))

    db.session.add_all(terms)
    db.session.commit()

