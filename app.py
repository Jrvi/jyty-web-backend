from flask import Flask
from extensions import db
from flask_cors import CORS
import os


def create_app():
    app = Flask(__name__)
    CORS(app)
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "jyty.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config['SECRET_KEY'] = 'salainen'

    db.init_app(app)

    # Models
    from models import User, Event, Announcement, PageContent

    # Rekisteröi reitit
    from routes.user_routes import user_bp
    from routes.event_routes import event_bp
    from routes.announcement_routes import announcement_bp
    from routes.content_routes import content_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(event_bp)
    app.register_blueprint(announcement_bp)
    app.register_blueprint(content_bp)

    return app
