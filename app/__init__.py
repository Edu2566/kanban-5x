import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev"
    app.config["SESSION_COOKIE_SAMESITE"] = "None"
    app.config["SESSION_COOKIE_SECURE"] = True
    os.makedirs(app.instance_path, exist_ok=True)
    db_path = os.path.join(app.instance_path, "kanban.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so that create_all can see them
    from .models import Empresa, Usuario, Column, Card  # noqa: F401

    # Create database tables if they don't exist yet
    with app.app_context():
        db.create_all()

    from .routes.main import main
    from .routes.webhook import webhook_bp
    from .routes.auth import auth_bp
    from .routes.superadmin import superadmin_bp
    app.register_blueprint(main)
    app.register_blueprint(webhook_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(superadmin_bp)

    return app
