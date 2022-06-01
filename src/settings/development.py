import os

from .config_base import ConfigBase


class Development(ConfigBase):
    DEBUG = True

    @property
    def config_files(self):
        return [
            os.path.join(
                self.APPLICATION_PACKAGE_ROOT, 'settings', "development.conf"
            )
        ]
