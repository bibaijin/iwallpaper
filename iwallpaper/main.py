import logging
import wx

from iwallpaper.config import CONFIG
from iwallpaper.model import Image
from iwallpaper.tray import TrayFrame
import iwallpaper.image_server as image_server


def main():
    logging.basicConfig(level=logging.INFO, format=CONFIG.log_format)
    CONFIG.makedirs()
    try:
        CONFIG.db.connect()
        CONFIG.db.create_tables([Image])
        daemon = image_server.Daemon()
        app = wx.App()
        TrayFrame(daemon).Iconize()
        daemon.start()
        app.MainLoop()
    finally:
        CONFIG.db.close()


if __name__ == "__main__":
    main()
