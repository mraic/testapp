from datetime import datetime, timezone, timedelta

import jwt
from flask import current_app

from src import User, AppLogException
from src.general import Status
from src.views import UserSchema


class UserService:

    def __init__(self, user=User()):
        self.user = user

    def create(self):

        if not UserService.check_if_email_exists(email=self.user.email):
            raise AppLogException(Status.user_with_email_exists())

        self.user.add()
        self.user.commit_or_rollback()

        return Status.successfully_processed()

    def deactivate(self):
        from src.domain import AccountService
        data = UserService.get_one(_id=self.user.id)

        if not data.user:
            raise AppLogException(Status.user_does_not_exists())

        if data.user.status == User.STATUSES.inactive:
            raise AppLogException(Status.user_is_deactivated_already())

        data.user.status = User.STATUSES.inactive

        accs = AccountService.get_all_accounts_for_user(self.user.id)

        for i in range(len(accs.account)):
            data_account = AccountService.get_one(_id=accs.account[i].id)
            AccountService.deactivate(data_account)

        self.user = data.user

        self.user.update()
        self.user.commit_or_rollback()

        return Status.successfully_processed()

    @staticmethod
    def login(acc_no, date, cvv):
        from src.domain import AccountService

        data = AccountService.login_with_card(acc_no=acc_no,
                                              date=date,
                                              cvv=cvv)

        data_card = AccountService.get_one_by_card_no_and_status(acc_no=acc_no)
        if data_card:
            raise AppLogException(Status.account_is_not_active())

        if not data:
            raise AppLogException(Status.wrong_credentials())

        data_user = UserService.get_one(_id=str(data.user_id))
        access_token, _ = UserService.generate_jwt_token(user_id=data.user_id,
                                                         account_id=data.id)
        schema = UserSchema()
        data_dict = schema.dump(data_user.user)
        data_dict['access_token'] = access_token

        return data_dict, Status.successfully_processed()

    @staticmethod
    def generate_jwt_token(user_id, account_id):
        try:
            access_token = jwt.encode({
                'id': str(user_id),
                'account_id': str(account_id),
                'exp': datetime.now(tz=timezone.utc) + timedelta(
                    seconds=current_app.config.get('JWT_EXPIRES_IN'))},
                current_app.config.get('JWT_SECRET_KEY'))

            return access_token, Status.successfully_processed()
        except Exception as e:
            raise e

    @classmethod
    def get_one(cls, _id):
        return cls(user=User.query.get_one(_id=_id))

    @staticmethod
    def check_if_email_exists(email):
        return User.query.check_if_email_exists(email=email)
