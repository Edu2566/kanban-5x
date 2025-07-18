import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev"
    db_path = os.path.join(app.instance_path, "kanban.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so that create_all can see them
    from .models import Empresa, Usuario, Column, Card  # noqa: F401

    from .routes import main
    from .webhook import webhook_bp
    from .auth import auth_bp
    from .superadmin import superadmin_bp

    app.register_blueprint(main)
    app.register_blueprint(webhook_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(superadmin_bp)

    return app