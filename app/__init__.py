from flask import Flask, request, session
from flask_login import LoginManager
from flask_babel import Babel, gettext
from flask_migrate import Migrate

from app.models import init_db, db
from app.models.user import User

import os

# -------------------------
# Supported languages
# -------------------------
SUPPORTED_LANGUAGES = ["en"]
# SUPPORTED_LANGUAGES = ["en", "zh_TW", "zh_CN", "fr", "ja"]


# -------------------------
# Locale selector
# -------------------------
def get_locale():
    # Return the user-selected language code (matches translation folder names)
    lang = session.get("lang")

    if lang in SUPPORTED_LANGUAGES:
        return lang

    return request.accept_languages.best_match(SUPPORTED_LANGUAGES) or "en"


# -------------------------
# App Factory
# -------------------------
def create_app():
    app = Flask(__name__)

    # -------------------------
    # CONFIG
    # -------------------------
    app.config["SECRET_KEY"] = "secret_key_1"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Babel config
    app.config["BABEL_DEFAULT_LOCALE"] = "en"
    app.config["BABEL_SUPPORTED_LOCALES"] = SUPPORTED_LANGUAGES
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    app.config["BABEL_TRANSLATION_DIRECTORIES"] = os.path.join(BASE_DIR, "..", "translations")

    # -------------------------
    # INIT DB
    # -------------------------
    init_db(app)

    migrate = Migrate(app, db)

    # -------------------------
    # LOGIN MANAGER
    # -------------------------
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # -------------------------
    # BABEL (FLASK-BABEL 4)
    # -------------------------
    babel = Babel(app, locale_selector=get_locale)

    # expose gettext globally for Jinja
    app.jinja_env.globals["_"] = gettext

    # expose locale to templates
    @app.context_processor
    def inject_globals():
        # Expose both the Babel locale (via get_locale) and the
        # user-facing language code stored in the session so templates
        # that expect 'zh_TW' / 'zh_CN' keep working.
        return {
            "get_locale": get_locale,
            "LANGUAGE": session.get("lang", "en")
        }

    # -------------------------
    # BLUEPRINTS
    # -------------------------
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.quiz import quiz_bp
    from app.routes.homepage import homepage_bp
    from app.routes.import_terms import import_bp
    from app.routes.language_switch import i18n_bp
    from app.routes.flashcard import flashcard_bp
    from app.routes.task_planner import taskplanner_bp
    from app.routes.settings import settings_bp

    # Not used yet
    # from app.routes.lecture import lecture_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(homepage_bp)
    app.register_blueprint(import_bp)
    app.register_blueprint(i18n_bp)
    app.register_blueprint(flashcard_bp)
    app.register_blueprint(taskplanner_bp)
    app.register_blueprint(settings_bp)

    # Not used yet
    # app.register_blueprint(lecture_bp)

    return app