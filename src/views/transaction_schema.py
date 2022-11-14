from marshmallow import fields
from marshmallow_enum import EnumField

from src import Transaction, AppLogException
from src.general import Status
from src.views import BaseSchema


def validate_amount(amount):
    if amount <= 0:
        raise AppLogException(Status.amount_must_positive())


class TransactionSchema(BaseSchema):
    id = fields.UUID(dump_only=True)
    amount = fields.Int(required=True, validate=validate_amount)
    date = fields.Date(dump_only=True)
    status = EnumField(Transaction.STATUSES, by_value=True, dump_only=True)
    account_id = fields.UUID(required=True)
    category_id = fields.UUID(required=True)


class UserTransactionSchema(TransactionSchema):
    class Meta:
        fields = ('amount', 'category_id',)


class ResponseOneTransactionSchema(BaseSchema):
    data = fields.Nested("TransactionSchema", dump_only=True)
    message = fields.Str(dump_only=True)


class Response_many_transaction_cat_total_schema(BaseSchema):
    category_id = fields.UUID(dump_only=True)
    total = fields.Int(dump_only=True)

class ResponseManyTransactionSchema(BaseSchema):
    data = fields.Nested("Response_many_transaction_cat_total_schema", many=True, dump_only=True)
    message = fields.Str(dump_only=True)


class TransactionBetweenAccountsSchema(BaseSchema):
    account_id = fields.UUID(required=True)
    amount = fields.Int(required=True, validate=validate_amount)
    category_id = fields.UUID(required=True)
    account_id_1 = fields.UUID(required=True)


class TransactionDateSchema(BaseSchema):
    date = fields.String(required=True)
    message = fields.Str(dump_only=True)


create_transaction_schema = TransactionSchema()
response_one_transaction_schema = ResponseOneTransactionSchema()
user_transaction_schema = UserTransactionSchema()
transaction_between_accounts_schema = TransactionBetweenAccountsSchema()
response_many_transaction_schema = ResponseManyTransactionSchema()
transaction_date_schema = TransactionDateSchema()
