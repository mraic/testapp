import enum
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import or_, func, orm
from sqlalchemy.dialects.postgresql import UUID

from src import db
from src.models.common import BaseModelMixin, ModelsMixin


class UserQuery(BaseModelMixin, db.Query):

    def get_one(self, _id):
        try:
            return self.filter(
                User.id == _id
            ).first()
        except Exception as e:
            db.session.rollback()
            raise e


class UserStatus(enum.Enum):
    active = 1
    inactive = 0


class User(BaseModelMixin, ModelsMixin, db.Model):
    __tablename__ = "users"
    query_class = UserQuery

    STATUSES = UserStatus

    id = sa.Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    first_name = sa.Column(sa.String(length=255), nullable=False)
    last_name = sa.Column(sa.String(length=255), nullable=False)
    email = sa.Column(sa.String(length=255), nullable=False)
    phone = sa.Column(sa.String(length=255), nullable=False)
    city = sa.Column(sa.String(length=255), nullable=False)
    status = sa.Column(
        sa.Enum(
            UserStatus,
            name='ck_user_status',
            native_enum=False,
            create_constraint=True,
            length=255,
            validate_strings=True
        ),
        nullable=False,
        default=UserStatus.active,
        server_default=UserStatus.active.name
    )
    accounts = orm.relationship("Account", back_populates="user")
