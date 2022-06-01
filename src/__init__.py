from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Flask
from flask_apispec import FlaskApiSpec

from . import cli
from .controller import bpp
from .db import db, migrate
from .general import build_error_response, CustomLogException, \
    DefaultAppException, AppLogException
from .models import *  # This one is important for Alembic auto generated migrations to work
from .settings import environments
import warnings
from werkzeug.exceptions import default_exceptions

#Dodati import router od svakoga controllera


def marshmallow_swagger_properties(self, field, **kwargs):
    """
    Add an OpenAPI extension for marshmallow instances
    """
    from marshmallow.fields import DateTime, Date, Time
    import marshmallow_enum
    from src.views import Hellper
    import arrow

    if isinstance(field, marshmallow_enum.EnumField):
        return {'type': 'string', 'enum': [m.value for m in field.enum]}

    elif isinstance(field, Time):
        return {
            'format': 'time',
            'example': arrow.utcnow().strftime(Hellper.time_format)}

    elif isinstance(field, Date):
        return {
            'format': 'date',
            'example': arrow.utcnow().strftime(Hellper.date_format)}

    elif isinstance(field, DateTime):
        return {
            'format': 'date-time',
            'example': arrow.utcnow().strftime(Hellper.datetime_format)}

    return {}


def create_app(config_environment):
    app = Flask(
        'App core',
        static_folder='./static',
        template_folder='./templates'
    )

    marshmallow_plugin = MarshmallowPlugin()
    app.config.update({
        'APISPEC_SPEC': APISpec(
            title='App core',
            version='v1',
            openapi_version='2.0',
            plugins=[marshmallow_plugin]
        ),
        'APISPEC_SWAGGER_URL': '/swagger',
        'APISPEC_SWAGGER_UI_URL': '/swagger-ui',
        'DEFAULT_MODEL_DEPTH': -1
    })
    marshmallow_plugin.converter.add_attribute_function(
        marshmallow_swagger_properties)
    docs = FlaskApiSpec(document_options=False)

    config_object = environments[config_environment]()
    config_object.init_app(app)

    db.init_app(app)
    migrate.init_app(
        app, db, directory=config_object.FLASK_MIGRATE_DB_DIRECTORY,
        compare_type=True)

    cli.Cli(app)

    # Mount blueprints
    app.register_blueprint(bpp)
    warnings.filterwarnings(
        "ignore",
        message="Multiple schemas resolved to the name "
    )

    # Log starting of application instance
    app.logger.info(
        "Starting Flask '{0}' in '{1}' mode".format(
            app.name, config_environment
        )
    )
    docs.init_app(app)
    _initialize_global_exception_handler(app)

    with app.test_request_context():
        for name, rule in app.view_functions.items():
            try:
                docs.register(rule, blueprint='bpp')
            except:
                pass

    return app


def _initialize_global_exception_handler(app):
    for code, ex in default_exceptions.items():
        app.errorhandler(code)(build_error_response)

    @app.errorhandler(400)
    def _unhandled_any_error(e):
        """
        Global, any-unhandled-exception handler.
        Returns API error JSON response.
        """
        return build_error_response(CustomLogException(
            e, 'ERROR_CODE_400_LOG_CATEGORY'))

    @app.errorhandler(404)
    def _unhandled_any_error(e):
        """
        Global, any-unhandled-exception handler.
        Returns API error JSON response.
        """
        return build_error_response(CustomLogException(
            e, 'ERROR_CODE_404_LOG_CATEGORY'))

    @app.errorhandler(405)
    def _unhandled_any_error(e):
        """
        Global, any-unhandled-exception handler.
        Returns API error JSON response.
        """
        return build_error_response(CustomLogException(
            e, 'ERROR_CODE_404_LOG_CATEGORY'))

    @app.errorhandler(422)
    def _unhandled_any_error(e):
        """
        Global, any-unhandled-exception handler.
        Returns API error JSON response.
        """
        return build_error_response(CustomLogException(
            e, 'ERROR_CODE_422_LOG_CATEGORY'))

    @app.errorhandler(500)
    def _unhandled_any_error(e):
        """
        Global, any-unhandled-exception handler.
        Returns API error JSON response.
        """
        return build_error_response(CustomLogException(
            e, 'ERROR_CODE_500_LOG_CATEGORY'))

    @app.errorhandler(Exception)
    def _unhandled_any_error(e):
        """
        Global, any-unhandled-exception handler.
        Returns API error JSON response.
        """
        return build_error_response(CustomLogException(
            e, 'DEFAULT_APP_LOG_CATEGORY'))

    @app.errorhandler(CustomLogException)
    def _unhandled_any_error(e):
        """
        Global, any-unhandled-exception handler.
        Returns API error JSON response.
        """
        return build_error_response(e)

    @app.errorhandler(DefaultAppException)
    def _unhandled_any_error(e):
        """
        Global, any-unhandled-exception handler.
        Returns API error JSON response.
        """
        return build_error_response(CustomLogException(
            e, 'DEFAULT_APP_LOG_CATEGORY'))

    @app.errorhandler(AppLogException)
    def _unhandled_any_error(e):
        """
        Global, any-unhandled-exception handler.
        Returns API error JSON response.
        """
        return build_error_response(
            CustomLogException(e, e.config_log_category_name))