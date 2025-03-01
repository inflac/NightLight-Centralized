from flask import Flask

from .db import db
from .models import Status

def preinitialize_statuses():
    """Pre-initialize default statuses if they don't exist."""
    default_statuses = [
        {"name": "default", "description_de": "Kein spezifischer Status gesetzt.", "description_en": "No specific status set."},
        {"name": "german", "description_de": "Heute sind wir nur auf Deutsch erreichbar 📞", "description_en": "Today we're only available in German 📞"},
        {"name": "english", "description_de": "Heute sind wir nur auf Englisch erreichbar 📞", "description_en": "Today we're only available in English 📞"},
        {"name": "german-english", "description_de": "Heute sind wir auf Deutsch und Englisch erreichbar 📞", "description_en": "Today we're available in German & English 📞"},
        {"name": "canceled", "description_de": "Wir sind heute Abend leider nicht erreichbar 🙁", "description_en": "Unfortunately, we're not available tonight 🙁"},
        {"name": "technical-issues", "description_de": "Aufgrund technischer Probleme sind wir nicht erreichbar ⚠️", "description_en": "Due to technical issues, we're currently unavailable ⚠️"}
    ]

    # TODO add try/except
    for status_data in default_statuses:
        existing_status = Status.query.filter_by(name=status_data["name"]).first()
        if not existing_status:
            new_status = Status(
                name=status_data["name"], 
                description_de=status_data["description_de"], 
                description_en=status_data["description_en"]
            )
            db.session.add(new_status)

    db.session.commit()