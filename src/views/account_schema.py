from marshmallow import fields
from marshmallow_enum import EnumField

from src import Account
from src.views import BaseSchema


class AccountSchema(BaseSchema):
    id = fields.UUID(dump_only=True)
    account_number = fields.Str(dump_only=True)
    expire_date = fields.Str(required=True)
    cvv = fields.Str(dump_only=True)
    amount = fields.Float(dump_only=True)
    status = EnumField(Account.STATUSES, by_value=True, dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    user_id = fields.UUID(required=True)


class AccountTransactionSchema(AccountSchema):
    transactions = fields.Nested("TransactionSchema", many=True)

class AccountTransactionFullSchema(AccountSchema):
    transactions = fields.Nested("TransactionSchema")

class ResponseOneAccountSchema(BaseSchema):
    data = fields.Nested("AccountTransactionSchema", dump_only=True)
    message = fields.Str(dump_only=True)


class ResponseManyAccountsSchema(BaseSchema):
    data = fields.Nested("AccountSchema", many=True, dump_only=True)
    message = fields.Str(dump_only=True)


class AlterExtendExpireDate(AccountSchema):
    class Meta:
        fields = ('expire_date',)


class AccountUserFilterSchema(BaseSchema):
    user_id = fields.UUID(required=True, allow_none=True)
    status = EnumField(Account.STATUSES, by_value=True, allow_none=True)


class UserFilterRequestAccountsSchema(BaseSchema):
    filter_data = fields.Nested("AccountUserFilterSchema")
    paginate_data = fields.Nested("PaginationSchema")


class GetAllUserPaginationDataAccountsSchema(BaseSchema):
    items = fields.Nested("AccountTransactionSchema", many=True, dump_only=True)
    total = fields.Int(dump_only=True)


class GetAllUserPaginateAccountSchema(BaseSchema):
    data = fields.Nested("GetAllUserPaginationDataAccountsSchema",
                         dump_only=True)
    message = fields.String(dump_only=True)


class AccountLoginSchema(BaseSchema):
    account_number = fields.Str(required=True)
    expire_date = fields.Str(required=True)
    cvv = fields.Str(required=True)


create_account_schema = AccountSchema()
response_one_account_schema = ResponseOneAccountSchema()
alter_account_schema = AlterExtendExpireDate()
request_user_filter_orders_schema = UserFilterRequestAccountsSchema()
get_all_user_pagination_data_accounts_schema = GetAllUserPaginateAccountSchema()
get_all_accounts_transactions_full_schema = None
account_login_schema = AccountLoginSchema()
response_many_accounts_schema = ResponseManyAccountsSchema
account_transaction_full_schema = AccountTransactionFullSchema()