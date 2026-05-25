from app.models import db
from app.models.sets import Term
from datetime import date, timedelta
from thefuzz import fuzz
import re

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

def normalize(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()

def check_similarity(correct_answer, user_response):
    correct_answer = normalize(correct_answer)
    user_response = normalize(user_response)

    similarity_score = fuzz.ratio(correct_answer, user_response)

    if (similarity_score >= 80 and len(user_response) >= 20) or correct_answer == user_response:
        return True
    else:
        return False
       