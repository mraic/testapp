import jwt
from flask import current_app, request
from flask_apispec import doc, use_kwargs, marshal_with

from src import bpp, Transaction
from src.domain import UserService, AccountService
from src.domain.transaction_domain import TransactionService
from src.general import allow_access, security_params, Status
from src.views import message_response_schema
from src.views.account_schema import account_login_schema, \
    response_many_accounts_schema, get_all_user_pagination_data_accounts_schema, \
    paginate_accounts_transaction_schema
from src.views.transaction_schema import response_one_transaction_schema, \
    user_transaction_schema, transaction_date_schema, \
    response_many_transaction_schema
from src.views.user_schema import response_one_user_token_schema


@doc(description="Login to user's account route", tags=["User"])
@bpp.post('/login')
@use_kwargs(account_login_schema, apply=True)
@marshal_with(response_one_user_token_schema, 200, apply=False)
@marshal_with(message_response_schema, 400, apply=True)
def login(**kwargs):
    user_data, status = UserService.login(acc_no=kwargs.get('account_number'),
                                          date=kwargs.get('expire_date'),
                                          cvv=kwargs.get('cvv'))

    return dict(message=status.message, data=user_data)


@doc(description="User account transaction route", params=security_params,
     tags=["User"])
@bpp.post('/transaction-payout')
@allow_access
@use_kwargs(user_transaction_schema, apply=True)
@marshal_with(response_one_transaction_schema, 200, apply=True)
@marshal_with(message_response_schema, 400, apply=True)
def user_transaction(**kwargs):
    token = request.environ.get('HTTP_AUTHORIZATION', None)

    payload = jwt.decode(
        token, current_app.config.get('JWT_SECRET_KEY'), algorithms=["HS256"])

    transaction_service = TransactionService(
        transaction=Transaction(
            account_id=payload['account_id'],
            amount=kwargs.get('amount'),
            category_id=kwargs.get('category_id')
        )
    )

    status = transaction_service.create()
    return dict(message=status.message, data=transaction_service.transaction)


@doc(description="Get all logged users accounts", params=security_params,
     tags=["User"])
@bpp.get('/get-accounts')
@allow_access
@marshal_with(response_many_accounts_schema, 200, apply=False)
@marshal_with(message_response_schema, 400, apply=True)
def get_accounts():
    token = request.environ.get('HTTP_AUTHORIZATION', None)

    payload = jwt.decode(
        token, current_app.config.get('JWT_SECRET_KEY'), algorithms=["HS256"])

    items = AccountService.get_all_accounts(user_id=payload['id'])
    return dict(data=items,
                message=Status.successfully_processed().message)


@doc(description="Get all logged users accounts", params=security_params,
     tags=["User"])
@bpp.get('/get-accounts-send-email')
@allow_access
@marshal_with(response_many_accounts_schema, 200, apply=False)
@marshal_with(message_response_schema, 400, apply=True)
def get_all_acc_email_sender_():
    token = request.environ.get('HTTP_AUTHORIZATION', None)

    payload = jwt.decode(
        token, current_app.config.get('JWT_SECRET_KEY'), algorithms=["HS256"])

    items = AccountService.get_all_acc_email_sender(user_id=payload['id'])
    return dict(data=items,
                message=Status.successfully_processed().message)


@doc(description='Paginate account orders route', params=security_params,
     tags=['User'])
@bpp.post('/user/account-transaction/paginate')
@allow_access
@use_kwargs(paginate_accounts_transaction_schema, apply=True)
@marshal_with(get_all_user_pagination_data_accounts_schema, 200, apply=True)
@marshal_with(message_response_schema, 400, apply=True)
def get_paginate_accounts_transactions(**kwargs):
    token = request.environ.get('HTTP_AUTHORIZATION', None)

    payload = jwt.decode(
        token, current_app.config.get('JWT_SECRET_KEY'), algorithms=["HS256"])
    filter_data = {
        "status": None,
        "account_id": payload['account_id']
    }

    items, total, status = AccountService.paginate_accounts_transactions(
        filter_data=filter_data, paginate_data=kwargs.get('paginate_data')
    )

    return dict(data=dict(items=items, total=total), message=status.message)


@doc(description="Generate excel file for current month",
     params=security_params,
     tags=['User'])
@bpp.get('/user/account-transaction/excel')
@allow_access
@marshal_with(message_response_schema, 400, apply=True)
def generate_excel_for_transactions():
    token = request.environ.get('HTTP_AUTHORIZATION', None)

    payload = jwt.decode(
        token, current_app.config.get('JWT_SECRET_KEY'), algorithms=["HS256"])

    return TransactionService.generate_and_download_excel(
        account_id=payload['account_id'])


@doc(description="Get all transaction category data",
     params=security_params,
     tags=['User'])
@bpp.post("/user/transaction-categories")
@allow_access
@use_kwargs(transaction_date_schema, apply=True)
@marshal_with(response_many_transaction_schema, 200, apply=True)
@marshal_with(message_response_schema, 400, apply=True)
def response_categories(**kwargs):
    data, status = TransactionService.get_transactions(date=kwargs.get('date'))
    return dict(data=data, message=status.message)
