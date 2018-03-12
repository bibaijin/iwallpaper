import logging

from iwallpaper.image_server import Wallhaven
from iwallpaper.config import CONFIG
from iwallpaper.model import Image


def main():
    logging.basicConfig(level=logging.INFO, format=CONFIG.log_format)
    CONFIG.makedirs()
    try:
        CONFIG.db.connect()
        CONFIG.db.create_tables([Image])
        w = Wallhaven()
        image = w.fetch_one()
        w.set_wallpaper(image)
        print(image)
    finally:
        CONFIG.db.close()


if __name__ == "__main__":
    main()
