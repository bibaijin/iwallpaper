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
        self.theta_file = '{}/theta.npy'.format(self.home)
        self.J_file = '{}/J.csv'.format(self.home)
        self.db = pw.SqliteDatabase('{}/iwallpaper.db'.format(self.home))
        self.log_format = '%(asctime)s - %(pathname)s:%(lineno)d - %(levelname)s - %(message)s'
        self.standard_height = 1080
        self.standard_width = 1920
        zoom_ratio = 10
        self.resized_height = int(self.standard_height / zoom_ratio)
        self.resized_width = int(self.standard_height / zoom_ratio)
        self.a1_number = 2 + self.resized_height * self.resized_width * 3
        self.a2_number = 20
        self.a3_number = 5

    def makedirs(self):
        for p in [self.download_home]:
            os.makedirs(p, exist_ok=True)


CONFIG = Config()
