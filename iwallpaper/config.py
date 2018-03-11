import os
import peewee as pw


class Config:
    def __init__(self):
        home = os.getenv('HOME')
        if home is None:
            raise Exception('$HOME not defined')

        xdg_config_home = os.getenv('XDG_CONFIG_HOME',
                                    '{}/.config'.format(home))
        self.home = '{}/iwallpaper'.format(xdg_config_home)
        self.download_home = '{}/downloads'.format(self.home)
        self.db = pw.SqliteDatabase('{}/iwallpaper.db'.format(self.home))
        self.log_format = '%(asctime)s - %(pathname)s:%(lineno)d - %(levelname)s - %(message)s'

    def makedirs(self):
        for p in [self.download_home]:
            os.makedirs(p, exist_ok=True)


CONFIG = Config()
