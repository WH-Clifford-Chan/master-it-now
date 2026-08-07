from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from app.models.user import User
from app.models import db
from app.utils import render_platform_template

import re

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/account_creation", methods=["GET", "POST"])
def account_creation():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username or not password:
            error = "Both username and password are required."
            return render_platform_template("auth", "account_creation.html", error=error)

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error = "Username already taken."
            return render_platform_template("auth", "account_creation.html", error=error)

        if len(password) < 8 and not re.search(r'[A-Z]', password):
            error = "Password must be more than 8 characters and contain at least more than one capital letter."
            return render_platform_template("auth", "account_creation.html", error=error)

        if len(password) < 8:
            error = "Password must be more than 8 characters."
            return render_platform_template("auth", "account_creation.html", error=error)

        if not re.search(r'[A-Z]', password):
            error = "Password must contain at least one capital letter."
            return render_platform_template("auth", "account_creation.html", error=error)

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("main.quizzes"))

    return render_platform_template("auth", "account_creation.html", error=error)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = False
    if current_user.is_authenticated:
        return redirect(url_for("main.flashcard_sets"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
    
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("main.flashcard_sets"))

        else:
            error = True

    return render_platform_template("auth", "login.html", error=error)

@auth_bp.route("/change_username", methods=["POST"])
@login_required
def change_username():
    user = User.query.filter_by(username=current_user.username).first()

    if not user:
        return redirect(url_for("settings.settings", error="user_not_found"))

    new_username = request.form.get("username", "").strip()

    # Validate empty username
    if not new_username:
        return redirect(url_for("settings.settings", error="username_empty"))

    # Check if username already exists
    existing_user = User.query.filter_by(username=new_username).first()
    if existing_user:
        return redirect(url_for("settings.settings", error="username_taken"))

    # No change needed case (optional but nice UX)
    if new_username == user.username:
        return redirect(url_for("settings.settings", error="username_same"))

    # Update username
    user.username = new_username
    db.session.commit()

    return redirect(url_for(
        "settings.settings",
        username_updated="true"
    ))


@auth_bp.route("/change_password", methods=["POST"])
@login_required
def change_password():
    user = User.query.filter_by(username=current_user.username).first()

    if not user:
        return redirect(url_for("settings.settings", error="user_not_found"))

    password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not check_password_hash(user.password, password):
        return redirect(url_for("settings.settings", error="wrong_password"))

    if new_password != confirm_password:
        return redirect(url_for("settings.settings", error="passwords_not_match"))

    user.password = generate_password_hash(new_password)
    db.session.commit()

    return redirect(url_for("settings.settings", password_updated="true"))

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))