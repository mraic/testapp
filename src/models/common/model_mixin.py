from sqlalchemy_utils.types.arrow import arrow
from ... import db


class ModelsMixin:

    @staticmethod
    def commit_or_rollback():
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def flush_or_rollback():
        try:
            db.session.flush()
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def flush():
        db.session.flush()

    def add(self):
        db.session.add(self)

    def update(self):
        self.updated_at = arrow.utcnow().datetime
        db.session.add(self)

    def delete(self):
        db.session.delete(self)

