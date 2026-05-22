from flask import Flask
from flask_login import LoginManager
from app.models import db, init_db
from app.models.user import User

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "secret_key_1"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize database
    init_db(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # import and register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.quiz import quiz_bp
    from app.routes.homepage import homepage_bp
    from app.routes.import_terms import import_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(homepage_bp)
    app.register_blueprint(import_bp)

    return app