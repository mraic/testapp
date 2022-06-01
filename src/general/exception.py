class DefaultAppException(Exception):
    def __init__(self, status):
        Exception.__init__(self, "{0}".format(status))
        self.status = status


class CustomLogException(Exception):
    def __init__(self, exception=None, config_log_category_name=None):
        self.exception = exception
        self.config_log_category_name = config_log_category_name \
            if config_log_category_name is not None \
            else 'DEFAULT_APP_LOG_CATEGORY'


class AppLogException(Exception):
    def __init__(self, status=None, config_log_category_name=None):
        self.status = status
        self.config_log_category_name = config_log_category_name \
            if config_log_category_name is not None \
            else 'DEFAULT_APP_LOG_CATEGORY'

