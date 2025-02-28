from db import db


class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(15), nullable=False)
    description_de = db.Column(db.String(200), nullable=False)
    description_en = db.Column(db.String(200), nullable=False)

    @classmethod
    def get_status(cls, status: str):
        """Query and return a status by name."""
        status = Status.query.filter_by(status=status).first()
        if not status:
            raise ValueError(f"Status '{status}' not found.")
        return status

    @classmethod
    def add_status(cls, status_name: str, description_de: str, description_en: str):
        """Add a new status to the db."""
        if Status.query.filter_by(status=status_name).first():
            raise ValueError(f"Status '{status_name}' already exists.")
        
        try:
            new_status = Status(status=status_name, description_de=description_de, description_en=description_en)
            db.session.add(new_status)
            db.session.commit()
            return new_status
        except Exception as e:
            db.session.rollback()
            raise RuntimeError(f"Error while adding the status: {str(e)}")

    @classmethod
    def remove_status(cls, status_name: str):
        """Remove a status from the db by its name."""
        status_to_remove = Status.query.filter_by(status=status_name).first()
        if not status_to_remove:
            raise ValueError(f"Status '{status_name}' does not exist.")
        
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
                'id': status.id,
                'status': status.status,
                'description_de': status.description_de,
                'description_en': status.description_en
            } for status in statuses]
            return status_list
        except Exception as e:
            raise RuntimeError(f"Error while fetching the statuses: {str(e)}")

    def __repr__(self):
        return f"Status('{self.status}')"
