
import os
import pwd

from .config_base import ConfigBase


class Production(ConfigBase):

    @property
    def config_files(self):
        return [
            os.path.join(
                self.APPLICATION_PACKAGE_ROOT, 'settings', "production.conf"
            )
        ]

    @property
    def config_files_old(self):
        user = pwd.getpwuid(os.getuid()).pw_name
        return [
            # ie. /etc/my_app.conf
            '/etc/{0}.conf'.format(self.APPLICATION_NAME),
            # ie. ~/.my_app.conf

            # The following relies on shell environment and thus will not work in
            # any non-interactive non-login shells (ie. under supervisord)
            # os.path.expanduser('~/.{0}.conf'.format(self.APPLICATION_NAME)),
            # instead, use pwd (UID and unix password file) to decypher home dir
            '/home/{0}/.{1}.conf'.format(user, self.APPLICATION_NAME),
        ]
