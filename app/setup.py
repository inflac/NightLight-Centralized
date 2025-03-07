from sqlalchemy.exc import SQLAlchemyError

from .db import db
from .models import Status

def preinitialize_statuses():
    from .logger import logger
    """Pre-initialize default statuses if they don't exist"""
    default_statuses = [
        {"name": "default",
         "description_de": "",
         "description_en": "",
         "description_now_de": "Wir sind jetzt erreichbar 📞",
         "description_now_en": "We're now available 📞"},
        {"name": "german",
         "description_de": "Heute sind wir nur auf Deutsch erreichbar 📞",
         "description_en": "Today we're only available in German 📞",
         "description_now_de": "Wir sind jetzt erreichbar, heute allerdings nur auf Deutsch 📞",
         "description_now_en": "We're now available but today only in German 📞"},
        {"name": "english",
         "description_de": "Heute sind wir nur auf Englisch erreichbar 📞",
         "description_en": "Today we're only available in English 📞",
         "description_now_de": "Wir sind jetzt erreichbar, heute allerdings nur auf Englisch 📞",
         "description_now_en": "We're now available but today only in English 📞"},
        {"name": "german-english",
         "description_de": "Heute sind wir auf Deutsch und Englisch erreichbar 📞",
         "description_en": "Today we're available in German & English 📞",
         "description_now_de": "Wir sind jetzt erreichbar, heute auf Deutsch und Englisch 📞",
         "description_now_en": "We're now available, today in German & English"},
        {"name": "canceled",
         "description_de": "Wir sind heute Abend leider nicht erreichbar 🙁",
         "description_en": "Unfortunately, we're not available tonight 🙁",
         "description_now_de": "Wir sind heute Abend leider nicht erreichbar 🙁",
         "description_now_en": "Unfortunately, we're not available tonight 🙁"},
        {"name": "technical-issues",
         "description_de": "Aufgrund technischer Probleme sind wir nicht erreichbar ⚠️",
         "description_en": "Due to technical issues, we're currently unavailable ⚠️",
         "description_now_de": "Aufgrund technischer Probleme sind wir nicht erreichbar ⚠️",
         "description_now_en": "Due to technical issues, we're currently unavailable ⚠️"}
    ]

    try:
        for status_data in default_statuses:
            existing_status = Status.query.filter_by(
                name=status_data["name"]).first()
            if not existing_status:
                new_status = Status(
                    name=status_data["name"],
                    description_de=status_data["description_de"],
                    description_en=status_data["description_en"],
                    description_now_de=status_data["description_now_de"],
                    description_now_en=status_data["description_now_en"]
                )
                db.session.add(new_status)
                logger.debug(f"Created status: {status_data["name"]}")

        db.session.commit()
        logger.info("Initilized statuses")

    except SQLAlchemyError as db_err:
        db.session.rollback()
        logger.error(f"Error while initializing statuses: {db_err}")
