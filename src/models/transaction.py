import enum
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import orm, func, desc
from sqlalchemy.dialects.postgresql import UUID

from src import db
from src.models.common import BaseModelMixin, ModelsMixin


class TransactionQuery(BaseModelMixin, db.Query):

    @staticmethod
    def get_all_trans_for_current_month(account_id, first_day, last_day):
        try:
            return db.session.query(
                Transaction
            ).filter(
                Transaction.account_id == account_id,
                Transaction.date.between(first_day, last_day)
            ).all()
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_category_name(category_id):
        from src import ListItem
        try:
            db.session.query(
                ListItem.name
            ).filter(
                ListItem.id == category_id
            ).first()
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_transactions(first_day, last_day):
        try:
            return db.session.query(
                Transaction.category_id,
                func.sum(Transaction.amount).label('total') if None else 0
            ).filter(
                Transaction.date.between(first_day, last_day)
            ).group_by(
                Transaction.category_id
            ).order_by(
                func.sum(desc(Transaction.amount).label('total'))
            ).all()
        except Exception as e:
            db.session.rollback()
            raise e


class TransactionStatus(enum.Enum):
    active = 1
    inactive = 0


class Transaction(BaseModelMixin, ModelsMixin, db.Model):
    __tablename__ = "transaction"
    query_class = TransactionQuery

    STATUSES = TransactionStatus

    id = sa.Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    amount = sa.Column(sa.Integer(), nullable=False)
    date = sa.Column(sa.Date())
    status = sa.Column(
        sa.Enum(
            TransactionStatus,
            name='ck_account_status',
            native_enum=False,
            create_constraint=True,
            length=255,
            validate_strings=True
        ),
        nullable=False,
        default=TransactionStatus.active,
        server_default=TransactionStatus.active.name
    )
    account_id = db.Column(UUID(as_uuid=True),
                           db.ForeignKey('accounts.id', ondelete="RESTRICT"),
                           nullable=False,
                           index=True)

    category_id = db.Column(UUID(as_uuid=True),
                            db.ForeignKey('listitems.id', ondelete="RESTRICT"),
                            nullable=False,
                            index=True)

    list_item = orm.relationship("ListItem", back_populates="transactions")

    account = orm.relationship("Account", back_populates="transactions",
                               uselist=False)
