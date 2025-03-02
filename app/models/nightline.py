from ..db import db
from .status import Status


class Nightline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    status_id = db.Column(
            db.Integer,
            db.ForeignKey('status.id'),
            nullable=False)
    status = db.relationship('Status', backref='cities')
    now = db.Column(db.Boolean, nullable=False, default=False)
    instagram_media_id = db.Column(db.String(50), nullable=True, default="")

    @classmethod
    def get_nightline(cls, name: str):
        """Query and return a nightline by name."""
        nightline = Nightline.query.filter_by(name=name).first()
        if not nightline:
            raise ValueError(f"Nightline '{name}' not found.")
        return nightline

    @classmethod
    def add_nightline(cls, name: str):
        """Create a new nightline with the default status."""
        default_status = Status.get_status("default")

        try:
            new_nightline = cls(name=name, status=default_status)
            db.session.add(new_nightline)
            db.session.commit()
            return new_nightline
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Error while adding the nightline: {str(e)}")

    @classmethod
    def remove_nightline(cls, name: str):
        """Remove a nightline from the database."""
        nightline = cls.query.filter_by(name=name).first()
        if not nightline:
            raise ValueError(f"Nightline '{name}' not found.")

        try:
            db.session.delete(nightline)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Error while removing the nightline: {str(e)}")

    @classmethod
    def list_cities(cls):
        """List all cities."""
        try:
            cities = Nightline.query.all()
            nightline_list = [{
                "id": nightline.id,
                "name": nightline.name,
                "status": nightline.status,
                "now": nightline.now,
            } for nightline in cities]
            return nightline_list
        except Exception as e:
            raise RuntimeError(f"Error while fetching the cities: {str(e)}")

    def set_status(self, name: str):
        """Set the status of a nightline by the status name."""
        new_status = Status.get_status(name)
        self.status = new_status
        db.session.commit()

    def reset_status(self):
        """Reset the status of a nightline to default."""
        new_status = Status.get_status("default")
        self.status = new_status
        db.session.commit()

    def set_now(self, now: bool):
        """Set now value of a nightline."""
        self.now = now
        db.session.commit()

    def __repr__(self):
        return f"Nightline('{self.name}')"
