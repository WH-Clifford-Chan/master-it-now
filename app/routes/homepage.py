from flask import Blueprint, redirect, url_for, request
from flask_login import current_user
from app.utils import render_platform_template

homepage_bp = Blueprint("homepage", __name__)

@homepage_bp.route("/")
def home():
    # Redirect logged-in users
    if current_user.is_authenticated:
        return redirect(url_for("main.quizzes"))

    # Show the appropriate homepage
    return render_platform_template("homepage.html")

