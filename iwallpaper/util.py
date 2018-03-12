import hashlib
import os

from iwallpaper.config import CONFIG


def hashsum(bytes):
    m = hashlib.sha256()
    m.update(bytes)
    return m.hexdigest()


def get_filetype(path):
    _, ext = os.path.splitext(path)
    return ext[1:]


def get_image_path(image_hashsum, image_filetype):
    return '{}/{}.{}'.format(CONFIG.download_home, image_hashsum,
                             image_filetype)
