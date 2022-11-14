import enum
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.dialects.postgresql import UUID

from src import db
from src.models.common import BaseModelMixin, ModelsMixin, BaseQueryMixin


class ListItemQuery(BaseQueryMixin, db.Query):

    def get_one(self, _id):
        try:
            return self.filter(
                ListItem.id == _id
            ).first()
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_category_prefix(_id):
        try:
            return db.session.query(
                ListItem
            ).filter(
                ListItem.id == _id,
                ListItem.prefix == '-'
            ).first() is not None
        except Exception as e:
            db.session.rollback()
            raise e


class ListItemStatus(enum.Enum):
    active = 1
    inactive = 0


class ListItem(BaseModelMixin, ModelsMixin, db.Model):
    __tablename__ = "listitems"
    query_class = ListItemQuery

    id = sa.Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    name = sa.Column(sa.String(length=255), nullable=False)
    description = sa.Column(sa.Text())
    prefix = sa.Column(sa.String(length=1))
    status = sa.Column(
        sa.Enum(
            ListItemStatus,
            name='ck_modellist_status',
            native_enum=False,
            create_constraint=True,
            length=255,
            validate_strings=True
        ),
        nullable=False,
        default=ListItemStatus.active,
        server_default=ListItemStatus.active.name
    )

    list_id = db.Column(UUID(as_uuid=True),
                        db.ForeignKey('lists.id', ondelete="RESTRICT"),
                        nullable=False,
                        index=True
                        )

    list = orm.relationship("List",
                            back_populates="list_item",
                            uselist=False)

    transactions = orm.relationship("Transaction",
                                    back_populates="list_item")
