import copy

import pytest

from src import AppLogException, Account
from src.domain import AccountService, TransactionService
from src.general import Status


@pytest.mark.usefixtures("dummy_user")
@pytest.mark.usefixtures("dummy_account")
@pytest.mark.usefixtures("dummy_transaction")
class TestTransactionService:

    def test_transaction_account(self, db, mocker):
        mock_account_get_one = mocker.patch(
            "src.domain.transaction_domain.AccountService."
            "get_one", autospec=True
        )

        mock_account_get_one.return_value = AccountService(
            account=self.dummy_account)

        mock_account_check_if_expired = mocker.patch(
            "src.domain.transaction_domain.AccountService."
            "check_if_account_expired", autospec=True
        )

        mock_account_check_if_expired.return_value = False

        mock_account_check_if_expired = mocker.patch(
            "src.domain.transaction_domain.ListItemService."
            "get_category_prefix", autospec=True
        )

        mock_account_check_if_expired.return_value = False

        transaction_domain = TransactionService(
            transaction=self.dummy_transaction)

        transaction_status = transaction_domain.create()

        assert transaction_status.message == Status.successfully_processed().message

    def test_create_transaction_no_acc(self, db, mocker):
        mock_account_get_one = mocker.patch(
            "src.domain.transaction_domain.AccountService."
            "get_one", autospec=True
        )

        mock_account_get_one.return_value = AccountService(
            account=None)

        transaction_domain = TransactionService(
            transaction=self.dummy_transaction)

        with pytest.raises(AppLogException) as ape:
            transaction_domain.create()

        assert ape.value.status.message == \
               Status.account_does_not_exists().message

    def test_account_expired(self, db, mocker):
        mock_account_get_one = mocker.patch(
            "src.domain.transaction_domain.AccountService."
            "get_one", autospec=True
        )

        mock_account_get_one.return_value = AccountService(
            account=self.dummy_account)

        mock_account_get_one = mocker.patch(
            "src.domain.transaction_domain.AccountService."
            "check_if_account_expired", autospec=True
        )

        mock_account_get_one.return_value = True

        transaction_domain = TransactionService(
            transaction=self.dummy_transaction)

        with pytest.raises(AppLogException) as ape:
            transaction_domain.create()

        assert ape.value.status.message == \
               Status.account_expired().message

    def test_account_status_inactive(self, db, mocker):
        mock_account_get_one = mocker.patch(
            "src.domain.transaction_domain.AccountService."
            "get_one", autospec=True
        )
        data = copy.deepcopy(self.dummy_account)
        data.status = Account.STATUSES.inactive
        mock_account_get_one.return_value = AccountService(
            account=data)

        mock_account_get_one = mocker.patch(
            "src.domain.transaction_domain.AccountService."
            "check_if_account_expired", autospec=True
        )

        mock_account_get_one.return_value = False

        transaction_domain = TransactionService(
            transaction=self.dummy_transaction)

        with pytest.raises(AppLogException) as ape:
            transaction_domain.create()

        assert ape.value.status.message == \
               Status.account_is_not_active().message

