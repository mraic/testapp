import enum
from datetime import datetime
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import orm, func
from sqlalchemy.dialects.postgresql import UUID

from src import db
from src.models.common import BaseModelMixin, ModelsMixin


class AccountQuery(BaseModelMixin, db.Query):

    def get_one(self, _id):
        try:
            return self.filter(
                Account.id == _id
            ).first()
        except Exception as e:
            db.session.rollback()
            raise e

    def check_if_exists(self, account_number):
        try:
            return self.filter(
                Account.account_number == account_number
            ).first() is not None
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def count_of_users_accounts(user_id):
        try:
            return db.session.query(
                Account
            ).filter(
                Account.user_id == user_id,
                Account.status == Account.STATUSES.active
            ).count()
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def check_if_account_expired(account_id):
        try:
            return db.session.query(
                Account
            ).filter(
                Account.id == account_id,
                Account.expire_date <= datetime.today()
            ).first() is not None
        except Exception as e:
            db.session.rollback()
            raise e

    def get_all_accounts_for_user(self, user_id):
        try:
            return self.filter(
                Account.user_id == user_id
            ).all()
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_full_account(account_id):
        from src import Transaction
        try:
            return db.session.query(
                Account,
                func.sum(Transaction.amount).label('amount')
            ).join(
                Transaction,
                Account.id == Transaction.account_id,
                isouter=True
            ).filter(
                Account.id == account_id
            ).group_by(
                Account.id
            ).first()
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_all_accounts(user_id):
        from src import Transaction
        try:
            return db.session.query(
                Account,
                func.sum(Transaction.amount).label('amount')
            ).join(
                Transaction,
                Account.id == Transaction.account_id,
                isouter=True
            ).filter(
                Account.user_id == user_id
            ).group_by(
                Account.id
            ).all()
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_paginated_account(filter_data, start, length, _id, status):
        try:
            return db.session.query(
                Account
            ).filter(
                filter_data,
                Account.user_id == _id,
                Account.status == status if None else True
            ).paginate(
                page=start, per_page=length, error_out=False, max_per_page=50)
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_paginated_transaction_for_account(filter_data, start, length, _id):
        from src import Transaction
        try:
            return db.session.query(
                Transaction
            ).filter(
                filter_data,
                Transaction.account_id == _id
            ).paginate(
                page=start, per_page=length, error_out=False, max_per_page=50)
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def login_with_card(acc_no, date, cvv):
        try:
            return db.session.query(
                Account
            ).filter(
                Account.account_number == acc_no,
                Account.expire_date == date,
                Account.cvv == cvv
            ).first()
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_one_by_card_no_and_status(acc_no):
        try:
            return db.session.query(
                Account
            ).filter(
                Account.account_number == acc_no,
                Account.status == Account.STATUSES.inactive
            ).first() is not None
        except Exception as e:
            db.session.rollback()
            raise e


class AccountStatus(enum.Enum):
    active = 1
    inactive = 0


class Account(BaseModelMixin, ModelsMixin, db.Model):
    __tablename__ = "accounts"
    query_class = AccountQuery

    STATUSES = AccountStatus

    id = sa.Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    account_number = sa.Column(sa.String(length=19), nullable=False)
    expire_date = sa.Column(sa.Date())
    cvv = sa.Column(sa.String(length=3), nullable=False)
    status = sa.Column(
        sa.Enum(
            AccountStatus,
            name='ck_account_status',
            native_enum=False,
            create_constraint=True,
            length=255,
            validate_strings=True
        ),
        nullable=False,
        default=AccountStatus.active,
        server_default=AccountStatus.active.name
    )

    user_id = db.Column(UUID(as_uuid=True),
                        db.ForeignKey('users.id', ondelete="RESTRICT"),
                        nullable=False,
                        index=True)

    user = orm.relationship("User", back_populates="accounts", uselist=False)
    transactions = orm.relationship("Transaction", back_populates="account")
