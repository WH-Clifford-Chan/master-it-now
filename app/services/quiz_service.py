from app.models import db
from app.models.sets import Term
from datetime import date

def update_term(term_id, is_correct):
    term = Term.query.filter_by(
        term_id=term_id
    ).first()

    if not term:
        return  

    if is_correct:
        term.score += 1
    else:
        term.score = 0

    term.last_learned = date.today()

    db.session.commit()

