import click
from flask.cli import with_appcontext


@click.group(
    name="db_migrations",
)
def db_migrations():
    pass


@db_migrations.command("test")
@with_appcontext
def db_migrations_test():
    print("This is a test!!")

