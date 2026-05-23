from app.models import db
from app.models.sets import Term
from datetime import date, timedelta

def update_term(term_id, is_correct):
    intervals = [1, 2, 4, 8, 15, 30]
    term = Term.query.filter_by(
        term_id=term_id
    ).first()
    today = date.today()

    if not term:
        return  
    
    due_date = term.due_date
    if not due_date:
        due_date = term.due_date or today

    if is_correct:
        if today < due_date:
            term.last_learned = today
            db.session.commit()
            return
        else:
            term.score += 1

            index = min(term.score, len(intervals) - 1)
            term.due_date = today + timedelta(days=intervals[index])

    else:
        term.score = 0
        term.due_date = today + timedelta(days=1)

    term.last_learned = today

    db.session.commit()


