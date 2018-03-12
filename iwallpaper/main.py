import logging
import wx

from iwallpaper.config import CONFIG
from iwallpaper.model import Image
from iwallpaper.tray import TrayFrame


def main():
    logging.basicConfig(level=logging.INFO, format=CONFIG.log_format)
    CONFIG.makedirs()
    app = wx.App()
    TrayFrame().Iconize()
    try:
        CONFIG.db.connect()
        CONFIG.db.create_tables([Image])
        app.MainLoop()
    finally:
        CONFIG.db.close()


if __name__ == "__main__":
    main()
