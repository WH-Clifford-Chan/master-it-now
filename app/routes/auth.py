from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from app.models.user import User
from app.models import db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/account_creation", methods=["GET", "POST"])
def account_creation():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username or not password:
            error = "Username and password are required."
            return render_template("account_creation.html", error=error)

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error = "Username already exists."
            return render_template("account_creation.html", error=error)

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("main.dashboard"))

    return render_template("account_creation.html", error=error)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = False
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
    
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("main.dashboard"))

        else:
            error = True

    return render_template("login.html", error=error)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))