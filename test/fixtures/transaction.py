import pytest
from faker import Faker

from src import Transaction


@pytest.fixture(scope="class")
def dummy_transaction(request, dummy_account):
    fake = Faker()

    request.cls.dummy_transaction = Transaction(
        id=fake.uuid4(),
        amount=fake.pyint(),
        date=fake.date(),
        account_id=dummy_account.id,
        category_id=fake.uuid4()

    )

    return request.cls.dummy_transaction
