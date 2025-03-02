from ..db import db


class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15), unique=True, nullable=False)
    description_de = db.Column(db.String(200), nullable=False)
    description_en = db.Column(db.String(200), nullable=False)
    description_now_de = db.Column(db.String(200), nullable=False)
    description_now_en = db.Column(db.String(200), nullable=False)

    @classmethod
    def get_status(cls, name: str):
        """Query and return a status by name."""
        status = Status.query.filter_by(name=name).first()
        if not status:
            raise ValueError(f"Status '{name}' not found.")
        return status

    @classmethod
    def add_status(cls, name: str, description_de: str, description_en: str, description_now_de: str, description_now_en: str):
        """Add a new status to the db."""
        if Status.query.filter_by(name=name).first():
            raise ValueError(f"Status '{name}' already exists.")

        try:
            new_status = Status(
                name=name,
                description_de=description_de,
                description_en=description_en,
                description_now_de=description_now_de,
                description_now_en=description_now_en)
            db.session.add(new_status)
            db.session.commit()
            return new_status
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Error while adding the status: {str(e)}")

    @classmethod
    def remove_status(cls, name: str):
        """Remove a status from the db by its name."""
        status_to_remove = Status.query.filter_by(name=name).first()
        if not status_to_remove:
            raise ValueError(f"Status '{name}' does not exist.")

        try:
            db.session.delete(status_to_remove)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Error while removing the status: {str(e)}")

    @classmethod
    def list_status(cls):
        """List all available statuses."""
        try:
            statuses = Status.query.all()
            status_list = [{
                "name": status.name,
                "description_de": status.description_de,
                "description_en": status.description_en,
                "description_now_de": status.description_now_de,
                "description_now_en": status.description_now_en,
            } for status in statuses]
            return status_list
        except Exception as e:
            raise RuntimeError(f"Error while fetching the statuses: {str(e)}")

    def __repr__(self):
        return f"Status('{self.name}')"
