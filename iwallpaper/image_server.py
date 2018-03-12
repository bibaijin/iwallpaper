import requests
import time
from lxml import html
import logging
import peewee as pw
import subprocess

import iwallpaper.model as model
import iwallpaper.util as util
from iwallpaper.config import CONFIG


class ImageServer:
    def fetch_one(self):
        raise NotImplementedError()

    def save(self, image_model, image_bytes):
        with open(self.get_image_path(image_model), 'wb') as f:
            f.write(image_bytes)

    def set_wallpaper(self, image_model):
        subprocess.run(['feh', '--bg-max', self.get_image_path(image_model)])

    def get_image_path(self, image_model):
        return '{}/{}.{}'.format(CONFIG.download_home, image_model.hashsum,
                                 image_model.filetype)


class Wallhaven(ImageServer):
    def __init__(self):
        self.random_url = 'https://alpha.wallhaven.cc/random'

    def fetch_one(self):
        r = requests.get(self.random_url)
        tree = html.fromstring(r.text)
        image_pages = tree.cssselect('a.preview')
        if len(image_pages) < 1:
            return None

        r = requests.get(image_pages[0].get('href'))
        tree = html.fromstring(r.text)
        images = tree.cssselect('#wallpaper')
        if len(images) < 1:
            return None

        image_url = 'https:{}'.format(images[0].get('src'))
        r = requests.get(image_url)
        image_hashsum = util.hashsum(r.content)
        image_filetype = util.get_filetype(image_url)
        try:
            image_model = model.Image.create(
                hashsum=image_hashsum,
                url=image_url,
                rank=0,
                filetype=image_filetype)
            self.save(image_model, r.content)
            return image_model
        except pw.IntegrityError as e:
            logging.error(
                'model.Image.create() failed, error: {}, will retry soon...'.
                format(e))
            time.sleep(1)
            return self.fetch_one()
