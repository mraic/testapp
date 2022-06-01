import enum
import inspect
import os
from datetime import date, datetime, timedelta

import arrow
import flask
import marshmallow
import sqlalchemy
import yaml


class Cli:
    def __init__(self, app: flask.Flask = None):
        if app:
            self.init_app(app)

    def init_app(self, app: flask.Flask = None):
        from .. import controller, models, settings
        from ..db import db
        from src import create_app
        from .migrations import db_migrations
        from .dev import db_dev

        if not app:
            return

        for command_group in [db_migrations]:
            app.cli.add_command(command_group)

        for command_group in [db_dev]:
            app.cli.add_command(command_group)

        @app.shell_context_processor
        def make_shell_context():
            retv = {
                # general modules
                "arrow": arrow,
                "enum": enum,
                "flask": flask,
                "marshmallow": marshmallow,
                "orm": sqlalchemy.orm,
                "os": os,
                "sa": sqlalchemy,
                "sqlalchemy": sqlalchemy,
                "yaml": yaml,
                # app modules
                "db": db,
                "models": models,
                "settings": settings,
                # convenient objects to have around
                "current_app": flask.current_app,
                "request": flask.request,
                "create_app": create_app,
                "print_sql": models.print_sql,
                "date": date,
                "datetime": datetime,
                "timedelta": timedelta,
                "joinedload": sqlalchemy.orm.joinedload,
                "selectinload": sqlalchemy.orm.selectinload,
                "contains_eager": sqlalchemy.orm.contains_eager,
            }

            modules = [
                models,
                controller,
            ]

            for module_ in modules:
                for k, v in inspect.getmembers(module_):
                    if not k.startswith("__") and not inspect.ismodule(v):
                        retv[k] = v

            return retv
