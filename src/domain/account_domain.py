from random import randint

from faker import Faker
from sqlalchemy import and_

from src import Account, AppLogException, User
from src.general import Status
from src.general.email_sender import created_bank_account, send_accounts_to_user
from src.views import AccountSchema


class AccountService:

    def __init__(self, account=Account()):
        self.account = account

    def create(self):
        from src.domain import UserService
        data = UserService.get_one(_id=self.account.user_id)

        if data.user is None:
            raise AppLogException(Status.user_does_not_exists())

        AccountService.count_of_users_accounts(user_id=self.account.user_id)

        acc_no, cvv = AccountService.generate_cred_no_cvv()

        self.account.account_number = acc_no
        self.account.cvv = cvv
        self.account.amount = 0

        self.account.add()
        self.account.commit_or_rollback()
        created_bank_account(bank_account=acc_no, recipients=data.user.email,
                             accounts=self.account)

        return Status.successfully_processed()

    def alter(self):

        data = AccountService.get_one(_id=self.account.id)

        if data.account is None:
            raise AppLogException(Status.account_does_not_exists())

        # if not AccountService.check_if_account_expired(data.account.id):
        #     raise AppLogException(Status.account_did_not_expire())

        data.account.amount = self.account.amount
        self.account = data.account

        self.account.update()
        self.account.commit_or_rollback()

        return Status.successfully_processed()

    def activate_account(self):

        data = AccountService.get_one(_id=self.account.id)

        if data.account is None:
            raise AppLogException(Status.account_does_not_exists())

        if data.account.status == Account.STATUSES.active:
            raise AppLogException(Status.account_is_already_activated())

        data.account.status = Account.STATUSES.active

        self.account = data.account

        self.account.update()
        self.account.commit_or_rollback()

        return Status.successfully_processed()

    def deactivate(self):

        data = AccountService.get_one(_id=self.account.id)

        if data.account is None:
            raise AppLogException(Status.account_does_not_exists())

        data.account.status = Account.STATUSES.inactive

        self.account = data.account

        self.account.update()
        self.account.commit_or_rollback()

        return Status.successfully_processed()

    @staticmethod
    def paginate_accounts(filter_data, paginate_data):
        filter_main = and_()
        if filter_data is not None:
            filter_main = and_(
                filter_main,
                User.id == filter_data.get('user_id')
                if filter_data.get('user_id') is not None else True,
                Account.status == filter_data.get('status')
                if filter_data.get('status') is not None else True)

        start = paginate_data.get('start') + 1 \
            if paginate_data is not None and paginate_data['start'] else 1

        length = paginate_data.get('length') \
            if paginate_data is not None and paginate_data['length'] else 10

        data = Account.query.get_paginated_account(
            filter_data=filter_main, start=start, length=length,
            _id=filter_data.get('user_id'),
            status=filter_data.get('status')
        )

        return data.items, data.total, Status.successfully_processed()

    @staticmethod
    def paginate_accounts_transactions(filter_data, paginate_data):
        filter_main = and_()
        if filter_data is not None:
            filter_main = and_(
                filter_main)

        start = paginate_data.get('start') \
            if paginate_data is not None and paginate_data['start'] else 1

        length = paginate_data.get('length') \
            if paginate_data is not None and paginate_data['length'] else 10

        data = Account.query.get_paginated_transaction_for_account(
            filter_data=filter_main, start=start, length=length,
            _id=filter_data.get('account_id'),
        )

        return data.items, data.total, Status.successfully_processed()

    @classmethod
    def get_one(cls, _id):
        return cls(account=Account.query.get_one(_id=_id))

    @staticmethod
    def check_if_exists(account_number):
        data = Account.query.check_if_exists(account_number=account_number)
        return data

    @staticmethod
    def generate_cred_no_cvv():
        fake = Faker()
        acc_numb = str(fake.credit_card_number(card_type='visa'))
        acc_numb = acc_numb[:4] + '-' + \
                   acc_numb[4:8] + '-' + \
                   acc_numb[8:12] + '-' + \
                   acc_numb[12:16]

        while AccountService.check_if_exists(account_number=acc_numb):
            acc_numb = str(fake.credit_card_number(card_type='visa'))
            acc_numb = acc_numb[:4] + '-' + \
                       acc_numb[4:8] + '-' + \
                       acc_numb[8:12] + '-' + \
                       acc_numb[12:16]

        cvv = randint(100, 999)

        return acc_numb, cvv

    @staticmethod
    def count_of_users_accounts(user_id):
        acc_no = Account.query.count_of_users_accounts(user_id=user_id)
        if acc_no >= 3:
            raise AppLogException(Status.user_has_max_accounts())

    @staticmethod
    def check_if_account_expired(account_id):
        data = Account.query.check_if_account_expired(account_id)
        return data

    @classmethod
    def get_all_accounts_for_user(cls, user_id):
        return cls(account=Account.query.get_all_accounts_for_user(
            user_id=user_id))

    @staticmethod
    def get_all_accounts(user_id):
        from src.domain import UserService
        user = UserService.get_one(_id=user_id)

        if user.user is None:
            raise AppLogException(Status.user_does_not_exists())

        data = Account.query_class.get_all_accounts(user_id=user_id)

        list_data = []
        schema = AccountSchema()
        for i in data or []:
            data_dict = schema.dump(i.Account)
            data_dict['amount'] = i.amount or 0
            list_data.append(data_dict)

        return list_data

    @staticmethod
    def get_all_acc_email_sender(user_id):
        from src.domain import UserService
        user = UserService.get_one(_id=user_id)

        if user.user is None:
            raise AppLogException(Status.user_does_not_exists())

        data = Account.query_class.get_all_accounts(user_id=user_id)
        send_accounts_to_user(recipients=user.user.email, accounts=data,
                              length=len(data))
        list_data = []
        schema = AccountSchema()
        for i in data or []:
            data_dict = schema.dump(i.Account)
            data_dict['amount'] = i.amount or 0
            list_data.append(data_dict)

        return list_data

    @staticmethod
    def login_with_card(acc_no, date, cvv):
        data = Account.query.login_with_card(acc_no=acc_no, date=date, cvv=cvv)
        return data

    @staticmethod
    def get_one_by_card_no_and_status(acc_no):
        data = Account.query.get_one_by_card_no_and_status(acc_no=acc_no)
        return data

    @staticmethod
    def get_full_account(account_id):
        data = Account.query.get_full_account(account_id=account_id)
        return data
