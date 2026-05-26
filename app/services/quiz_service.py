from app.models import db
from app.models.sets import Card
from datetime import date, timedelta
from thefuzz import fuzz
import re

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
       