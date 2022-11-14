from types import SimpleNamespace

import pytest

from src import AppLogException
from src.domain import AccountService, UserService
from src.general import Status
from src.models.account import AccountQuery


@pytest.mark.usefixtures("dummy_user")
@pytest.mark.usefixtures("dummy_account")
class TestAccountService:

    def test_create_account(self, db, mocker):
        mock_get_users_acc = mocker.patch(
            "src.domain.account_domain.AccountService."
            "count_of_users_accounts", autospec=True
        )

        mock_get_users_acc.return_value = 0

        mock_created_bank_account = mocker.patch(
            "src.domain.account_domain.created_bank_account", autospec=True
        )
        mock_created_bank_account.return_value = True

        mock_generate_cred_no_cvv = mocker.patch(
            "src.domain.account_domain.AccountService."
            "generate_cred_no_cvv", autospec=True
        )

        mock_generate_cred_no_cvv.return_value = \
            self.dummy_account.account_number, self.dummy_account.cvv

        account_domain = AccountService(account=self.dummy_account)

        account_status = account_domain.create()

        assert account_status.message == Status.successfully_processed().message

    def test_account_create_user_none(self, db, mocker):
        mock_get_user = mocker.patch(
            "src.domain.account_domain.UserService."
            "get_one", autospec=True
        )

        mock_get_user.return_value = UserService(user=None)

        account_domain = AccountService(account=None)

        with pytest.raises(AppLogException) as ape:
            account_domain.create()

        assert ape.value.status.message == \
               Status.user_does_not_exists().message

    def test_alter(self, db, mocker):
        mock_get_account = mocker.patch(
            "src.domain.account_domain.AccountService."
            "get_one", autospec=True
        )

        mock_get_account.return_value = AccountService(
            account=self.dummy_account)

        account_domain = AccountService(account=self.dummy_account)

        account_status = account_domain.alter()

        assert account_status.message == Status.successfully_processed().message

    def test_alter_acc_no_exists(self, db, mocker):
        mock_get_account = mocker.patch(
            "src.domain.account_domain.AccountService."
            "get_one", autospec=True
        )

        mock_get_account.return_value = AccountService(
            account=None)

        account_domain = AccountService(account=self.dummy_account)

        with pytest.raises(AppLogException) as ape:
            account_domain.alter()

        assert ape.value.status.message == \
               Status.account_does_not_exists().message

    def test_deactivate(self, db, mocker):
        mock_get_account = mocker.patch(
            "src.domain.account_domain.AccountService."
            "get_one", autospec=True
        )

        mock_get_account.return_value = AccountService(
            account=self.dummy_account)

        account_domain = AccountService(account=self.dummy_account)

        account_status = account_domain.deactivate()

        assert account_status.message == Status.successfully_processed().message

    def test_deactivate_account_does_not_exists(self, db, mocker):
        mock_get_account = mocker.patch(
            "src.domain.account_domain.AccountService."
            "get_one", autospec=True
        )

        mock_get_account.return_value = AccountService(
            account=None)

        account_domain = AccountService(account=self.dummy_account)

        with pytest.raises(AppLogException) as ape:
            account_domain.deactivate()

        assert ape.value.status.message == \
               Status.account_does_not_exists().message

    def test_paginate_account(self, db, mocker):
        mock_accounts = mocker.patch.object(
            AccountQuery,
            'get_paginated_account', autospec=True
        )

        total_mock = 1

        mock_accounts.return_value = SimpleNamespace(
            items=[self.dummy_account], total=total_mock
        )
        paginate_data = dict(length=0, start=0)

        filter_data = {
            "status": None,
            "user_id": self.dummy_account.user_id

        }

        items, total, status = AccountService.paginate_accounts(
            filter_data=filter_data, paginate_data=paginate_data,
        )

        assert status.message == Status.successfully_processed().message
        assert total == total_mock

    def test_paginate_account_transactions(self, db, mocker):
        mock_accounts = mocker.patch.object(
            AccountQuery,
            'get_paginated_transaction_for_account', autospec=True
        )

        total_mock = 1

        mock_accounts.return_value = SimpleNamespace(
            items=[self.dummy_account], total=total_mock
        )
        paginate_data = dict(length=0, start=0)

        filter_data = {
            "status": None,
            "account_id": self.dummy_account.id
        }

        items, total, status = AccountService.paginate_accounts_transactions(
            filter_data=filter_data, paginate_data=paginate_data,
        )

        assert status.message == Status.successfully_processed().message
        assert total == total_mock
