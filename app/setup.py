from flask import Flask

from config import Config
from db import db
from models import Status

def preinitialize_statuses():
    """Pre-initialize default statuses if they don't exist."""
    default_statuses = [
        {"status": "default", "description_de": "Kein spezifischer Status gesetzt.", "description_en": "No specific status set."},
        {"status": "german", "description_de": "Heute sind wir nur auf Deutsch erreichbar 📞", "description_en": "Today we're only available in German 📞"},
        {"status": "english", "description_de": "Heute sind wir nur auf Englisch erreichbar 📞", "description_en": "Today we're only available in English 📞"},
        {"status": "german-english", "description_de": "Heute sind wir auf Deutsch und Englisch erreichbar 📞", "description_en": "Today we're available in German & English 📞"},
        {"status": "canceled", "description_de": "Wir sind heute Abend leider nicht erreichbar 🙁", "description_en": "Unfortunately, we're not available tonight 🙁"},
        {"status": "technical-issues", "description_de": "Aufgrund technischer Probleme sind wir nicht erreichbar ⚠️", "description_en": "Due to technical issues, we're currently unavailable ⚠️"}
    ]

    for status_data in default_statuses:
        existing_status = Status.query.filter_by(status=status_data["status"]).first()
        if not existing_status:
            new_status = Status(
                status=status_data["status"], 
                description_de=status_data["description_de"], 
                description_en=status_data["description_en"]
            )
            db.session.add(new_status)

    db.session.commit()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Set up logging
    Config.configure_logging()

    # Configure CORS
    Config.configure_cors(app)

    db.init_app(app)

    with app.app_context():
        db.create_all()
        preinitialize_statuses()

    return app