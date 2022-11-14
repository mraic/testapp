import io
import os
from datetime import datetime

import pandas as pd
from flask import Response

from src import Transaction, AppLogException, Account
from src.domain import AccountService
from src.domain.list_idem_domain import ListItemService
from src.general import Status
from src.views import TransactionSchema, AccountSchema


class TransactionService:

    def __init__(self, transaction=Transaction()):
        self.transaction = transaction

    def create(self):
        data = AccountService.get_one(_id=self.transaction.account_id)

        if data.account is None:
            raise AppLogException(Status.account_does_not_exists())

        if AccountService.check_if_account_expired(data.account.id):
            raise AppLogException(Status.account_expired())

        if data.account.status == Account.STATUSES.inactive:
            raise AppLogException(Status.account_is_not_active())

        category_data = ListItemService.get_one(
            _id=self.transaction.category_id)

        if category_data.listitem is None:
            raise AppLogException(Status.category_does_not_exists())

        if ListItemService.get_category_prefix(
                _id=self.transaction.category_id):

            if data.account.amount < self.transaction.amount:
                raise AppLogException(Status.insufficient_funds())

            self.transaction.amount = - self.transaction.amount
            acc = AccountService.get_one(_id=self.transaction.account_id)
            acc.account.amount += self.transaction.amount
            acc.alter()
        else:

            acc = AccountService.get_one(_id=self.transaction.account_id)
            acc.account.amount += self.transaction.amount
            acc.alter()

        self.transaction.date = datetime.today()
        self.transaction.add()
        self.transaction.commit_or_rollback()

        return Status.successfully_processed()

    @staticmethod
    def generate_and_download_excel(account_id):

        data_account = AccountService.get_one(_id=account_id)

        if data_account.account is None:
            raise AppLogException(Status.account_does_not_exists())

        transaction = TransactionSchema(many=True).dump(
            data_account.account.transactions)

        first_date = datetime(datetime.today().year, datetime.today().month, 1)
        last_date = datetime(datetime.today().year, datetime.today().month + 1,
                             1)

        transactions = TransactionService.get_all_trans_for_current_month(
            account_id,
            first_day=first_date,
            last_day=last_date)

        data = {
            'Account amount': data_account.account.amount,
            'Transaction amount': [],
            'Transaction date': [],
            'Transaction category': [],
        }

        for i in transactions:
            cat = i.list_item.name

        for i in range(len(transaction)):
            data['Transaction amount'].append(transaction[i]['amount'])
            data['Transaction date'].append(transaction[i]['date'])
            data['Transaction category'].append(cat)

        df_transaction = pd.DataFrame(data,
                                      columns=['Account amount',
                                               'Transaction amount',
                                               'Transaction date',
                                               'Transaction category'])

        df_transaction.set_index('Account amount', inplace=True)

        df_transaction.to_excel(f'{data_account.account.account_number}.xlsx',
                                header=True)
        buffer = io.BytesIO()
        df = pd.read_excel(f'{data_account.account.account_number}.xlsx',
                           header=0)
        df.to_excel(buffer)

        headers = {
            f'Content-Disposition': f'attachment; filename={data_account.account.account_number}.xlsx',
            'Content-type': 'application/vnd.ms-excel'
        }
        os.remove(f'{data_account.account.account_number}.xlsx')

        return Response(buffer.getvalue(), mimetype='application/vnd.ms-excel',
                        headers=headers)

    @staticmethod
    def transfer_between_accounts(amount, account_id,
                                  account_id_1, category_id):
        acc = AccountService.get_one(_id=account_id)
        acc1 = AccountService.get_one(_id=account_id_1)

        if not (acc.account or acc1.account):
            raise AppLogException(Status.account_does_not_exists())

        if acc.account.user_id != acc1.account.user_id:
            raise AppLogException(Status.accounts_must_have_same_owner())

        if acc1.account.status == Account.STATUSES.inactive:
            raise AppLogException(Status.account_is_not_active())

        if acc.account.amount < amount:
            raise AppLogException(Status.insufficient_funds())

        transaction_service = TransactionService(
            transaction=Transaction(
                amount=amount,
                account_id=acc.account.id,
                category_id=category_id
            )
        )
        transaction_service.create()

        acc.account.amount + amount
        acc.alter()

        transaction_service = TransactionService(
            transaction=Transaction(
                amount=amount,
                account_id=acc1.account.id,
                category_id='67a2aaa0-c307-4869-a3a4-8e934a888c3f'
            )
        )
        transaction_service.create()

        acc1.account.amount + amount
        acc1.alter()

        data = [acc, acc1]

        list_data = []
        schema = AccountSchema()
        for i in data or []:
            current_dict = schema.dump(i.account)

            list_data.append(current_dict)

        return list_data, Status.successfully_processed()

    @staticmethod
    def get_all_trans_for_current_month(account_id, first_day, last_day):
        data = Transaction.query.get_all_trans_for_current_month(
            account_id=account_id,
            first_day=first_day,
            last_day=last_day)

        return data

    @staticmethod
    def get_category_name(category_id):
        data = Transaction.query.get_category_name(category_id=category_id)
        return data

    @staticmethod
    def get_transactions(date):
        date = date
        date = datetime.strptime(date,
                                 '%m/%y')

        first_date = datetime(date.year, date.today().month, 1)
        last_date = datetime(date.year, date.today().month + 1,
                             1)
        data = Transaction.query.get_transactions(first_day=first_date,
                                                  last_day=last_date)

        list_data = []
        schema = TransactionSchema()
        for i in data or []:
            current_dict = schema.dump(i)
            current_dict['total'] = i.total or 0
            list_data.append(current_dict)

        return list_data, Status.successfully_processed()
