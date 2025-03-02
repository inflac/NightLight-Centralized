from ..db import db
from .status import Status


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    status_id = db.Column(
        db.Integer,
        db.ForeignKey('status.id'),
        nullable=False)
    status = db.relationship('Status', backref='cities')
    instagram_media_id = db.Column(db.String(50), nullable=True, default="")

    @classmethod
    def get_city(cls, name: str):
        """Query and return a city by name."""
        city = City.query.filter_by(name=name).first()
        if not city:
            raise ValueError(f"City '{name}' not found.")
        return city

    @classmethod
    def add_city(cls, name: str):
        """Create a new city with the default status."""
        default_status = Status.get_status("default")

        try:
            new_city = cls(name=name, status=default_status)
            db.session.add(new_city)
            db.session.commit()
            return new_city
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Error while adding the city: {str(e)}")

    @classmethod
    def remove_city(cls, name: str):
        """Remove a city from the database."""
        city = cls.query.filter_by(name=name).first()
        if not city:
            raise ValueError(f"City '{name}' not found.")

        try:
            db.session.delete(city)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Error while removing the city: {str(e)}")

    @classmethod
    def list_cities(cls):
        """List all cities."""
        try:
            cities = City.query.all()
            city_list = [{
                'id': city.id,
                'name': city.name,
                'status': city.status,
            } for city in cities]
            return city_list
        except Exception as e:
            raise RuntimeError(f"Error while fetching the cities: {str(e)}")

    def __repr__(self):
        return f"City('{self.name}')"
