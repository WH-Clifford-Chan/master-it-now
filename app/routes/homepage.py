from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

homepage_bp = Blueprint("homepage", __name__)

@homepage_bp.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("main.quizzes"))
    return render_template("homepage.html")

