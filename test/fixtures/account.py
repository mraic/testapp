import pytest
from faker import Faker

from src import Account


@pytest.fixture(scope="class")
def dummy_account(request):
    fake = Faker()
    acc_numb = str(fake.credit_card_number(card_type='visa'))
    acc_numb = acc_numb[:4] + '-' + \
               acc_numb[4:8] + '-' + \
               acc_numb[8:12] + '-' + \
               acc_numb[12:16]

    request.cls.dummy_account = Account(
        id=fake.uuid4(),
        account_number=acc_numb,
        expire_date=fake.credit_card_expire(),
        cvv=fake.credit_card_security_code(),
        amount=fake.pyint()
    )

    return request.cls.dummy_account
