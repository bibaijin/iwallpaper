import datetime
import requests
import time
from lxml import html
import logging
import os
import peewee as pw
import subprocess
import threading

import iwallpaper.model as model
import iwallpaper.util as util
import iwallpaper.ai as ai


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
                self.__clean()

    def __clean(self):
        old_day = datetime.datetime.now() - datetime.timedelta(days=3)
        query = model.Image.select().where(model.Image.updated_at < old_day,
                                           model.Image.rank < 5)
        for image in query:
            self.__delete_image(image)

    def __delete_image(self, image):
        logging.info('Image: {} will be deleted...'.format(image))
        try:
            os.remove(util.get_image_path(image.hashsum, image.filetype))
            logging.info('Image: {} has been deleted.'.format(image))
        except Exception as e:
            logging.error('os.remove() failed, error: {}.'.format(e))
        finally:
            image.delete_instance()

    def delete_image(self):
        if self.image is None:
            return self.next_image()

        self.__delete_image(self.image)
        return self.next_image()

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
            self.predict_rank = ai.NETWORK.predict(images[0])
            return

        query = model.Image.select().where(
            model.Image.id > self.image.id,
            model.Image.is_deleted == False).order_by(model.Image.id).limit(1)
        images = [image for image in query]
        if len(images) != 1:
            self.__download_one(self.__image_servers[0])
            return self.next_image()

        self.__set_wallpaper(images[0])
        self.image = images[0]
        self.predict_rank = ai.NETWORK.predict(images[0])
        return

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
        self.predict_rank = ai.NETWORK.predict(images[0])
        return self.image

    def rank_image(self, rank):
        if self.image is None:
            return None

        logging.info('Image: {} will be ranked as {}.'.format(
            self.image, rank))
        self.image.rank = rank
        self.image.updated_at = datetime.datetime.now()
        self.image.save()
        logging.info('Image: {} has been ranked as {}.'.format(
            self.image, rank))

        self.__fit()
        return self.image

    def __fit(self):
        lambda_ = 1
        query = model.Image.select().where(model.Image.rank > 0)
        images = [image for image in query]
        ai.NETWORK.fit(images, lambda_)

    def __set_wallpaper(self, image):
        subprocess.run([
            'feh', '--bg-max',
            util.get_image_path(image.hashsum, image.filetype)
        ])
        logging.info('{} has been set as wallpaper.'.format(image))
