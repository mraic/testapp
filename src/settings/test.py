import os

from .config_base import ConfigBase


class Test(ConfigBase):
    DEBUG = True
    TESTING = True

    @property
    def config_files(self):
        return [
            os.path.join(
                self.APPLICATION_PACKAGE_ROOT, 'settings', "test.conf"
            )
        ]
