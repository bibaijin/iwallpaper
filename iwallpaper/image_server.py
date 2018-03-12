import datetime
import requests
import time
from lxml import html
import logging
import peewee as pw
import subprocess
import threading

import iwallpaper.model as model
import iwallpaper.util as util


class ImageServer:
    def download_one(self):
        raise NotImplementedError()

    def save(self, image_hashsum, image_url, image_bytes):
        image_filetype = util.get_filetype(image_url)
        with open(util.get_image_path(image_hashsum, image_filetype),
                  'wb') as f:
            f.write(image_bytes)
        return model.Image.create(
            hashsum=image_hashsum,
            url=image_url,
            rank=0,
            filetype=image_filetype)


class Wallhaven(ImageServer):
    home = 'https://alpha.wallhaven.cc'

    def __init__(self):
        self.__random_url = '{}/random'.format(self.home)

    def download_one(self):
        try:
            r = requests.get(self.__random_url)
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
            return self.save(image_hashsum, image_url, r.content)
        except Exception as e:
            logging.error(
                'Wallhaven.download_one() failed, error: {}, will retry soon...'.
                format(e))
            time.sleep(1)
            return self.download_one()


class Daemon(threading.Thread):
    __image_servers = [Wallhaven()]

    def __init__(self):
        threading.Thread.__init__(self)
        self.image = None

    def run(self):
        while True:
            for server in self.__image_servers:
                time.sleep(300)
                self.__download_one(server)

    def __download_one(self, server):
        logging.info('Downloading a wallpaper from {}...'.format(server.home))
        image = server.download_one()
        logging.info('{} has been downloaded from {}.'.format(
            image, server.home))

    def next_image(self):
        if self.image is None:
            query = model.Image.select().order_by(pw.fn.Random()).limit(1)
            images = [image for image in query]
            if len(images) != 1:
                self.__download_one(self.__image_servers[0])
                return self.next_image()

            self.__set_wallpaper(images[0])
            self.image = images[0]
            return self.image

        query = model.Image.select().where(
            model.Image.id > self.image.id,
            model.Image.is_deleted == False).order_by(model.Image.id).limit(1)
        images = [image for image in query]
        if len(images) != 1:
            self.__download_one(self.__image_servers[0])
            return self.next_image()

        self.__set_wallpaper(images[0])
        self.image = images[0]
        return self.image

    def previous_image(self):
        if self.image is None:
            return None

        query = model.Image.select().where(
            model.Image.id < self.image.id,
            model.Image.is_deleted == False).order_by(
                model.Image.id.desc()).limit(1)
        images = [image for image in query]
        if len(images) != 1:
            return None

        self.__set_wallpaper(images[0])
        self.image = images[0]
        return self.image

    def delete_image(self):
        if self.image is None:
            return self.next_image()

        self.image.is_deleted = True
        self.image.updated_at = datetime.datetime.now()
        self.image.save()
        return self.next_image()

    def rank_image(self, rank):
        if self.image is None:
            return None

        logging.info('{} will be ranked as {}.'.format(self.image, rank))
        self.image.rank = rank
        self.image.updated_at = datetime.datetime.now()
        self.image.save()
        return self.image

    def __set_wallpaper(self, image):
        subprocess.run([
            'feh', '--bg-max',
            util.get_image_path(image.hashsum, image.filetype)
        ])
        logging.info('{} has been set as wallpaper.'.format(image))
