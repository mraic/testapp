import copy

import pytest

from src import AppLogException, User
from src.domain import UserService, AccountService
from src.general import Status


@pytest.mark.usefixtures("dummy_account")
@pytest.mark.usefixtures("dummy_user")
class TestUserService:

    def test_create_user(self, db, mocker):
        user_domain = UserService(user=self.dummy_user)

        user_status = user_domain.create()

        assert user_status.message == Status.successfully_processed().message

    def test_deactivate_user(self, db, mocker):
        mock_user_service_get_one = mocker.patch(
            "src.domain.user_domain.UserService."
            "get_one", autospec=True
        )

        mock_user_service_get_one.return_value = UserService(
            user=self.dummy_user)

        user_domain = \
            UserService(user=self.dummy_user)

        user_status = user_domain.deactivate()

        assert user_status.message == Status.successfully_processed().message

    def test_deactivate_user_exists(self, db, mocker):
        mock_user_service_get_one = mocker.patch(
            "src.domain.user_domain.UserService."
            "get_one", autospec=True
        )

        mock_user_service_get_one.return_value = UserService(
            user=None)

        user_domain = \
            UserService(user=self.dummy_user)

        with pytest.raises(AppLogException) as ape:
            user_domain.deactivate()

        assert ape.value.status.message == \
               Status.user_does_not_exists().message

    def test_deactivate_user_inactive(self, db, mocker):
        mock_user_service_get_one = mocker.patch(
            "src.domain.user_domain.UserService."
            "get_one", autospec=True
        )

        data = copy.deepcopy(self.dummy_user)
        data.status = User.STATUSES.inactive
        mock_user_service_get_one.return_value = UserService(
            user=data)

        user_domain = \
            UserService(user=self.dummy_user)

        with pytest.raises(AppLogException) as ape:
            user_domain.deactivate()

        assert ape.value.status.message == \
               Status.user_is_deactivated_already().message

    def test_login(self, db, mocker):
        mock_account_service_login_with_card = mocker.patch(
            "src.domain.account_domain.AccountService."
            "login_with_card", autospec=True
        )
        data = copy.deepcopy(self.dummy_account)
        setattr(data, 'user_id', self.dummy_user.id)

        mock_account_service_login_with_card.return_value = AccountService(
            account=data)

        mock_user_service_get_one = mocker.patch(
            "src.domain.user_domain.UserService."
            "get_one", autospec=True
        )

        mock_user_service_get_one.return_value = UserService(
            user=self.dummy_user.id)

        mock_user_service_jwt_token = mocker.patch(
            "src.domain.user_domain.UserService."
            "generate_jwt_token", autospec=True
        )

        mock_user_service_jwt_token.return_value = None, \
                                                   Status.successfully_processed()

        user_domain = \
            UserService(user=self.dummy_user)

        data, status_login = UserService.login(
            acc_no=self.dummy_account.account_number,
            date=self.dummy_account.expire_date,
            cvv=self.dummy_account.cvv)

        assert data.status == Status.successfully_processed().message

    def test_login_wrong_creds(self, db, mocker):
        mock_account_service_login_with_card = mocker.patch(
            "src.domain.account_domain.AccountService."
            "login_with_card", autospec=True
        )
        data = copy.deepcopy(self.dummy_account)
        setattr(data, 'user_id', self.dummy_user.id)

        mock_account_service_login_with_card.return_value = AccountService(
            account=None)
        

        mock_user_service_get_one = mocker.patch(
            "src.domain.user_domain.UserService."
            "get_one", autospec=True
        )

        mock_user_service_get_one.return_value = UserService(
            user=self.dummy_user.id)

        mock_user_service_jwt_token = mocker.patch(
            "src.domain.user_domain.UserService."
            "generate_jwt_token", autospec=True
        )

        mock_user_service_jwt_token.return_value = None, \
                                                   Status.successfully_processed()

        user_domain = \
            UserService(user=self.dummy_user)

        with pytest.raises(AppLogException) as ape:
            user_domain.login(
                acc_no=self.dummy_account.account_number,
                cvv=self.dummy_account.cvv,
                date=self.dummy_account.expire_date,
            )

        assert ape.value.status.message == \
               Status.wrong_credentials().message


    def test_generate_jwt_token(self, db, mocker):
        mock_user = mocker.patch(
            "src.domain.user_domain.UserService."
            "get_one", autospec=True
        )

        mock_user.return_value = UserService.get_one(_id=self.dummy_user.id)

        mock_account = mocker.patch(
            "src.domain.account_domain.AccountService."
            "get_one", autospec=True)

        mock_account.return_value = AccountService.get_one(
            _id=self.dummy_user.id)

        access_token, status = UserService.generate_jwt_token(
            user_id=self.dummy_user.id,
            account_id=self.dummy_account.id)

        assert status.message == Status.successfully_processed().message
        assert type(access_token) == str and len(access_token) > 25
