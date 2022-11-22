from flask_apispec import doc, marshal_with, use_kwargs

from src import bpp, Account, User, Transaction
from src.domain import AccountService, UserService
from src.domain.transaction_domain import TransactionService
from src.views import message_response_schema
from src.views.account_schema import response_one_account_schema, \
    create_account_schema, alter_account_schema, \
    request_user_filter_orders_schema, \
    get_all_user_pagination_data_accounts_schema, response_many_accounts_schema
from src.views.transaction_schema import create_transaction_schema, \
    response_one_transaction_schema, transaction_between_accounts_schema
from src.views.user_schema import response_one_user_schema, create_user_schema


@doc(description="Create user route", tags=["Bank"])
@bpp.post('/bank/create-user')
@use_kwargs(create_user_schema, apply=True)
@marshal_with(response_one_user_schema, 200, apply=True)
@marshal_with(message_response_schema, 400, apply=True)
def create_user(**kwargs):
    user_service = UserService(
        user=User(
            first_name=kwargs.get('first_name'),
            last_name=kwargs.get('last_name'),
            email=kwargs.get('email'),
            phone=kwargs.get('phone'),
            city=kwargs.get('city'),
        )
    )
    status = user_service.create()

    return dict(data=user_service.user, message=status.message)


@doc(description="Create account route", tags=["Bank"])
@bpp.post('/bank/create-account')
@use_kwargs(create_account_schema, apply=True)
@marshal_with(response_one_account_schema, 200, apply=True)
@marshal_with(message_response_schema, 400, apply=True)
def create_account(**kwargs):
    account_service = AccountService(
        account=Account(
            expire_date=kwargs.get('expire_date'),
            user_id=kwargs.get('user_id')
        )
    )
    status = account_service.create()

    return dict(message=status.message, data=account_service.account)


@doc(description="Extend account expire date", tags=["Bank"])
@bpp.put('/bank/alter-expire-account/<uuid:account_id>')
@use_kwargs(alter_account_schema, apply=True)
@marshal_with(response_one_account_schema, 200, apply=True)
@marshal_with(message_response_schema, 400, apply=True)
def extend_account(account_id, **kwargs):
    account_service = AccountService(
        account=Account(
            id=account_id,
            expire_date=kwargs.get('expire_date'),
        )
    )
    status = account_service.alter()

    return dict(message=status.message, data=account_service.account)


@doc(description="Deactivate user", tags=["Bank"])
@bpp.put('/bank/deactivate-user/<uuid:user_id>')
@marshal_with(response_one_user_schema, 200, apply=True)
@marshal_with(message_response_schema, 400, apply=True)
def deactivate_user(user_id):
    user_service = UserService(
        user=User(
            id=user_id,
        )
    )
    status = user_service.deactivate()

    return dict(message=status.message, data=user_service.user)


@doc(description="Deactivate user's account", tags=["Bank"])
@bpp.put('/bank/deactivate-account/<uuid:account_id>')
@marshal_with(response_one_account_schema, 200, apply=True)
@marshal_with(message_response_schema, 400, apply=True)
def deactivate_users_account(account_id):
    account_service = AccountService(
        account=Account(
            id=account_id
        )
    )
    status = account_service.deactivate()

    return dict(message=status.message, data=account_service.account)


@doc(description="Activate user's account", tags=["Bank"])
@bpp.put('/bank/activate-account/<uuid:account_id>')
@marshal_with(response_one_account_schema, 200, apply=True)
@marshal_with(message_response_schema, 400, apply=True)
def activate_users_account(account_id):
    account_service = AccountService(
        account=Account(
            id=account_id
        )
    )
    status = account_service.activate_account()

    return dict(message=status.message, data=account_service.account)


@doc(description='Paginate user orders route',
     tags=['Bank'])
@bpp.post('/user/account/paginate')
@use_kwargs(request_user_filter_orders_schema, apply=True)
@marshal_with(get_all_user_pagination_data_accounts_schema, 200, apply=True)
@marshal_with(message_response_schema, 400, apply=True)
def get_paginate_user_accs(**kwargs):
    filter_data = kwargs.get('filter_data')
    paginate_data = kwargs.get('paginate_data')

    items, total, status = AccountService.paginate_accounts(
        filter_data=filter_data, paginate_data=paginate_data
    )

    return dict(data=dict(items=items, total=total), message=status.message)


@doc(description="Create transaction route", tags=["Bank"])
@bpp.post('/bank/create-transaction')
@use_kwargs(create_transaction_schema, apply=True)
@marshal_with(response_one_transaction_schema, 200, apply=True)
@marshal_with(message_response_schema, 400, apply=True)
def create_transaction(**kwargs):
    transaction_service = TransactionService(
        transaction=Transaction(
            amount=kwargs.get('amount'),
            account_id=kwargs.get('account_id'),
            category_id=kwargs.get('category_id')
        )
    )
    status = transaction_service.create()

    return dict(message=status.message, data=transaction_service.transaction)


@doc(description="Transaction between accounts route", tags=["Bank"])
@bpp.post('/bank/create-transaction-between-accounts')
@use_kwargs(transaction_between_accounts_schema, apply=True)
@marshal_with(response_many_accounts_schema, 200, apply=False)
@marshal_with(message_response_schema, 400, apply=True)
def create_transactions_between_accs(**kwargs):
    data, status = TransactionService.transfer_between_accounts(
        account_id=kwargs.get('account_id'), amount=kwargs.get('amount'),
        account_id_1=kwargs.get('account_id_1'),
        category_id=kwargs.get('category_id'))

    return dict(data=data, message=status.message)
