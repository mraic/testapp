import datetime

import click
from faker import Faker
from flask.cli import with_appcontext

from src import User


@click.group(
    name="db_migrations",
)
def db_migrations():
    pass


@db_migrations.command("test")
@with_appcontext
def db_migrations_test():
    print("This is a test!!")


@db_migrations.command("generate_categories")
@with_appcontext
def db_generate_data_migration():
    from src import List, ListItem, Account

    faker = Faker()

    list_1 = List(
        name="Category",
        description="Transaction category for decreasing amount of money"
    )

    list_1.add()
    list_1.commit_or_rollback()

    list_2 = List(
        name="Category",
        description="Transaction category for increasing amount of money"
    )

    list_2.add()
    list_2.commit_or_rollback()

    list_item_1 = ListItem(
        name='Plaća',
        description="Plaća",
        prefix='+',
        list_id=list_2.id
    )

    list_item_1.add()
    list_item_1.commit_or_rollback()

    list_item_2 = ListItem(
        name='Hrana',
        description="Hrana",
        prefix='-',
        list_id=list_1.id
    )

    list_item_2.add()
    list_item_2.commit_or_rollback()

    list_item_3 = ListItem(
        name='Međuračunsko plaćanje',
        description="Međuračunsko plaćanje",
        prefix='-',
        list_id=list_1.id
    )

    list_item_3.add()
    list_item_3.commit_or_rollback()

    list_item_4 = ListItem(
        name='Transport',
        description="Transport",
        prefix='-',
        list_id=list_1.id
    )

    list_item_4.add()
    list_item_4.commit_or_rollback()

    list_item_5 = ListItem(
        name='Zdravlje',
        description="Zdravlje",
        prefix='-',
        list_id=list_1.id
    )

    list_item_5.add()
    list_item_5.commit_or_rollback()

    list_item_6 = ListItem(
        name='Odjeća',
        description="Odjeća",
        prefix='-',
        list_id=list_1.id
    )

    list_item_6.add()
    list_item_6.commit_or_rollback()

    list_item_3 = ListItem(
        id='67a2aaa0-c307-4869-a3a4-8e934a888c3f',
        name='Međuračunsko plaćanje',
        description="Međuračunsko plaćanje",
        prefix='+',
        list_id=list_2.id
    )

    list_item_3.add()
    list_item_3.commit_or_rollback()

    print("Categories successfully created")

    for i in range(5):
        user = User(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            email=faker.email(),
            city=faker.city(),
            phone=faker.phone_number(),
        )
        user.add()
        user.commit_or_rollback()

        for j in range(2):
            acc_numb = str(faker.credit_card_number(card_type='visa'))
            acc_numb = acc_numb[:4] + '-' + \
                       acc_numb[4:8] + '-' + \
                       acc_numb[8:12] + '-' + \
                       acc_numb[12:16]

            cvv = faker.credit_card_security_code()
            int(str(cvv)[:2])

            account = Account(
                account_number=acc_numb,
                cvv=cvv,
                expire_date=datetime.date(2023, 1, 1),
                amount=0,
                user_id=user.id
            )
            account.add()
            account.commit_or_rollback()

    print("User created successfully")
    print("Accounts created successfully")