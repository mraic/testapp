import enum
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.dialects.postgresql import UUID

from src import db
from src.models.common import BaseModelMixin, ModelsMixin


class ListStatus(enum.Enum):
    active = 1
    inactive = 0


class List(BaseModelMixin, ModelsMixin, db.Model):
    __tablename__ = "lists"

    id = sa.Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    name = sa.Column(sa.String(length=255), nullable=False)
    description = sa.Column(sa.Text())
    status = sa.Column(
        sa.Enum(
            ListStatus,
            name='ck_modellist_status',
            native_enum=False,
            create_constraint=True,
            length=255,
            validate_strings=True
        ),
        nullable=False,
        default=ListStatus.active,
        server_default=ListStatus.active.name
    )

    list_item = orm.relationship("ListItem", back_populates="list")