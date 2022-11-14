import pytest
from faker import Faker

from src import User

@pytest.fixture(scope="class")
def dummy_user(request):
    fake = Faker()

    request.cls.dummy_user = User(
        id=fake.uuid4(),
        first_name=fake.user_name(),
        last_name=fake.last_name(),
        email=fake.email(),
        phone=fake.phone_number(),
        city=fake.address()
    )

    return request.cls.dummy_user