import configparser
import logging
import logging.handlers
import os
import socket
from datetime import datetime
import pytz
import tzlocal
from flask_cors import CORS
from unipath import Path


class ImproperlyConfiguredError(RuntimeError):
    pass


class ContextFilter(logging.Filter):
    HOSTNAME = socket.gethostname()

    def filter(self, record):
        record.hostname = ContextFilter.HOSTNAME
        record.isotime_utc = datetime.fromtimestamp(
            record.created, tzlocal.get_localzone()
        ).astimezone(pytz.utc).isoformat()
        return True


class ConfigBase:
    APPLICATION_NAME = 'App core'

    # --------------------------------------------------------------------------
    # Application directories
    # --------------------------------------------------------------------------
    APPLICATION_PACKAGE_ROOT = Path(os.path.dirname(os.path.realpath(__file__))
                                    ).ancestor(1)
    APPLICATION_REPO_ROOT = APPLICATION_PACKAGE_ROOT.ancestor(1)

    # Where wsgi.py is found
    APPLICATION_PACKAGE_ROOT = APPLICATION_PACKAGE_ROOT
    # Where controller.py is found
    APPLICATION_REPO_ROOT = APPLICATION_REPO_ROOT
    # Directory for logs if local logging is configured
    LOGS_ROOT = APPLICATION_REPO_ROOT.child('log')
    # Temporary directories
    TEMP_ROOT = APPLICATION_REPO_ROOT.child('tmp')
    CACHE_ROOT = TEMP_ROOT.child('cache')

    # --------------------------------------------------------------------------
    # Flask config
    # --------------------------------------------------------------------------
    SECRET_KEY = None
    JWT_EXPIRES_IN = None
    JWT_SECRET_KEY = None

    # --------------------------------------------------------------------------
    # Flask settings
    # --------------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # Flask-Migrate config
    # --------------------------------------------------------------------------
    FLASK_MIGRATE_DB_DIRECTORY = APPLICATION_PACKAGE_ROOT.child('db').child(
        'migrations')

    # --------------------------------------------------------------------------
    # Flask-SQLAlchemy config
    # --------------------------------------------------------------------------
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # If set to True SQLAlchemy will log all the statements issued to stderr
    # which can be useful for debugging.
    # We are setting this to False because SQLAlchemy tries to log UTF-8 data
    # as Latin1 logger which then causes chaos further down the stack
    # Instead all this, we manage SQLAlchemy loggers on our own - redirecting
    # these messages to file (ie. development.sqlalchemy.log)
    SQLALCHEMY_ECHO = False
    LOG_SQL = True

    # --------------------------------------------------------------------------
    # Logging config
    # --------------------------------------------------------------------------
    FILELOG_ENABLED = True
    FILELOG_LOGLEVEL = None
    SYSLOG_LOGLEVEL = None
    SYSLOG_ADDRESS = None
    SYSLOG_FACILITY = None
    SYSLOG_SOCKET_TYPE = None
    FILELOG_FORMAT = \
        u'[%(asctime)s] [PID: %(process)s] [{0}] %(levelname)s: %(message)s'.\
            format(APPLICATION_NAME)
    SYSLOG_FORMAT = \
        '%(isotime_utc)s %(hostname)s {0}[%(process)d]: %(levelname)s %(message)s'.\
            format(APPLICATION_NAME)

    ADDITIONAL_LOGGERS = [
        'alembic',
        'werkzeug',
        # 'sqlalchemy',
        'sqlalchemy.engine',
    ]
    def read_config_file(self):
        config_parser = configparser.ConfigParser()
        if not config_parser.read(self.config_files):
            raise ImproperlyConfiguredError('No config file found')

        section = config_parser['Database']
        self.SQLALCHEMY_DATABASE_URI = section.get('sqlalchemy_uri',
                                                   fallback='')

        section = config_parser['Settings']
        ##################################

        section = config_parser['Flask']
        self.SECRET_KEY = section.get('secret_key', fallback='')
        self.JWT_EXPIRES_IN = section.getint('jwt_expires_in_seconds',
                                             fallback=45)
        self.JWT_SECRET_KEY = section.get('jwt_secret_key', fallback = '')
        section = config_parser['Logging']
        self.FILELOG_LOGLEVEL = section.get('filelog_loglevel',
                                            fallback='debug')
        self.SYSLOG_LOGLEVEL = section.get('syslog_loglevel', fallback='debug')
        self.SYSLOG_ADDRESS = section.get('syslog_address', fallback=None)
        self.SYSLOG_FACILITY = section.get('syslog_facility', fallback='local1')
        self.SYSLOG_SOCKET_TYPE = section.get('syslog_socket_type',
                                              fallback='UDP')

    def validate(self):
        errors = dict()

        if not self.SQLALCHEMY_DATABASE_URI:
            errors['SQLALCHEMY_DATABASE_URI'] = "Can't be blank"

        if not self.APPLICATION_NAME:
            errors['APPLICATION_NAME'] = "Can't be blank"

        if errors:
            raise ImproperlyConfiguredError(errors)

    @property
    def file_log_path(self):
        return self.APPLICATION_REPO_ROOT.child('log').child(
            type(self).__name__.lower() + '.log'
        )

    def file_log_handler(self, file_path):
        handler = logging.handlers.WatchedFileHandler(
            filename=(file_path or self.file_log_path)
        )
        handler.setFormatter(logging.Formatter(self.FILELOG_FORMAT))
        handler.setLevel({'info': logging.INFO,
                          'critical': logging.CRITICAL,
                          'warning': logging.WARNING,
                          'debug': logging.DEBUG,
                          'error': logging.ERROR,}[
                             self.FILELOG_LOGLEVEL.lower()])
        return handler

    def syslog_log_handler(self):
        handler = logging.NullHandler()
        if self.SYSLOG_ADDRESS:
            if ':' in self.SYSLOG_ADDRESS:
                ip, port = self.SYSLOG_ADDRESS.split(':')
                syslog_address = tuple([ip, int(port)])
            else:
                syslog_address = self.SYSLOG_ADDRESS

            handler = logging.handlers.SysLogHandler(
                address=syslog_address, facility=self.SYSLOG_FACILITY,
                socktype={'tcp': socket.SOCK_STREAM,
                          'udp': socket.SOCK_DGRAM,}[
                    self.SYSLOG_SOCKET_TYPE.lower()]
            )
            handler.setFormatter(logging.Formatter(self.SYSLOG_FORMAT))

        handler.setLevel({'info': logging.INFO,
                          'critical': logging.CRITICAL,
                          'warning': logging.WARNING,
                          'debug': logging.DEBUG,
                          'error': logging.ERROR,}[
                             self.SYSLOG_LOGLEVEL.lower()])

        handler.addFilter(ContextFilter())

        return handler

    def _cleanup_logger_handlers(self, logger):
        while logger.handlers:
            logger.removeHandler(logger.handlers[0])

    def _init_loggers(self, app):
        # Our own handlers
        handlers = []
        if self.FILELOG_ENABLED:
            handlers.append(self.file_log_handler(file_path=self.file_log_path))
        if self.SYSLOG_ADDRESS:
            handlers.append(self.syslog_log_handler())

        # loggers we are interested in
        loggers = set(
            [app.logger] + [
                logging.getLogger(logger_name)
                for logger_name in self.ADDITIONAL_LOGGERS
            ]
        )

        # Explicitly shut down SQLAlchemy loggers even if they are not
        # enumerated in self.ADDITIONAL_LOGGERS
        # We will check self.LOG_SQL and configre them below
        self._cleanup_logger_handlers(logging.getLogger('sqlalchemy'))
        self._cleanup_logger_handlers(logging.getLogger('sqlalchemy.engine'))

        for logger in loggers:
            if 'sql' not in logger.name.lower():
                self._cleanup_logger_handlers(logger)
                # logger should pass all messages to handler, and handlers' log
                # level then decides what will be logged.
                logger.setLevel(logging.DEBUG)
                for handler in handlers:
                    logger.addHandler(handler)

        logger = logging.getLogger('sqlalchemy')
        logger.addHandler(logging.NullHandler())

        if self.LOG_SQL:
            logger = logging.getLogger('sqlalchemy.engine')
            logger.setLevel(logging.INFO)
            logger.setLevel(logging.DEBUG)
            for handler in handlers:
                logger.addHandler(handler)

    def init_app(self, app):
        if app:
            self.read_config_file()
            self.validate()
            app.config.from_object(self)
            self._init_loggers(app)
            CORS(app)



