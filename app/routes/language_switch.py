from flask import Blueprint, redirect, request, session, url_for

i18n_bp = Blueprint("i18n", __name__)

@i18n_bp.route("/lang/<lang>")
def set_language(lang):
    supported = ["en", "zh_TW", "zh_CN", "fr", "ja"]

    if lang not in supported:
        lang = "en"

    session["lang"] = lang

    return redirect(request.referrer or url_for("main.flashcards"))


