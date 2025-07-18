from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kanban.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Import models so that create_all can see them
    from .models import Empresa, Usuario, Column, Card  # noqa: F401

    from .routes import main
    from .webhook import webhook_bp
    app.register_blueprint(main)
    app.register_blueprint(webhook_bp)

    with app.app_context():
        db.create_all()

    return app
