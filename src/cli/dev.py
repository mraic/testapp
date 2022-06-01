import click
import flask
from sqlalchemy import text
from sqlalchemy_utils import database_exists, drop_database, create_database
from flask.cli import with_appcontext
from src.cli.common import confirm_if_not_dev


@click.group(
    name="db_dev",
)
def db_dev():
    pass


@db_dev.command("recreate")
@with_appcontext
def dev_db_recreate_command():
    """Drop and create database"""
    confirm_if_not_dev("Recreate database")
    dev_app = flask.current_app
    dev_db_url = dev_app.config["SQLALCHEMY_DATABASE_URI"]
    if database_exists(dev_db_url):
        print(f"{dev_db_url} exits. Dropping it...")
        drop_database(dev_db_url)
    print(f"Creating {dev_db_url}")
    create_database(dev_db_url)
    print("Done! Remember that you still need to run 'flask db upgrade'")


@db_dev.command("create")
@with_appcontext
def dev_db_create_command():
    """Create database"""
    confirm_if_not_dev("Create database")
    dev_app = flask.current_app
    dev_db_url = dev_app.config["SQLALCHEMY_DATABASE_URI"]
    print(f"Creating {dev_db_url}")
    create_database(dev_db_url)
    print("Done! Remember that you still need to run 'flask db upgrade'")


@db_dev.command("drop")
@with_appcontext
def dev_db_drop_command():
    """Drop database"""
    confirm_if_not_dev("Drop database")
    dev_app = flask.current_app
    dev_db_url = dev_app.config["SQLALCHEMY_DATABASE_URI"]
    print(f"Dropping {dev_db_url}")
    drop_database(dev_db_url)


@db_dev.command("truncate")
@with_appcontext
def dev_db_truncate_command():
    """Truncate all tables in database."""
    from ..db import helpers

    confirm_if_not_dev("Truncate database")
    db = flask.current_app.extensions["sqlalchemy"].db
    helpers.truncate_db(db)


@db_dev.command("create_postgis_extension")
@with_appcontext
def dev_db_create_postgis_extension():
    db = flask.current_app.extensions["sqlalchemy"].db
    sql = text('CREATE EXTENSION postgis')
    db.engine.execute(sql)

