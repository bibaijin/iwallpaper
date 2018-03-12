import wx
import wx.adv
import logging

import iwallpaper.image_server as image_server


class TrayIcon(wx.adv.TaskBarIcon):
    TBMENU_NEXT = wx.NewId()
    TBMENU_PREVIOUS = wx.NewId()
    TBMENU_RANK_5 = wx.NewId()
    TBMENU_RANK_4 = wx.NewId()
    TBMENU_RANK_3 = wx.NewId()
    TBMENU_RANK_2 = wx.NewId()
    TBMENU_RANK_1 = wx.NewId()
    TBMENU_RANK_0 = wx.NewId()
    TBMENU_CLOSE = wx.NewId()

    def __init__(self, frame):
        wx.adv.TaskBarIcon.__init__(self)
        self.frame = frame

        img = wx.Image('favicon.ico', wx.BITMAP_TYPE_ANY)
        bmp = wx.Bitmap(img)
        self.icon = wx.Icon()
        self.icon.CopyFromBitmap(bmp)
        self.SetIcon(self.icon, 'iWallpaper')
        self.Bind(wx.EVT_MENU, self.OnNext, id=self.TBMENU_NEXT)
        self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=self.TBMENU_CLOSE)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.OnTaskBarLeftClick)

        self.wallhaven = image_server.Wallhaven()

    def CreatePopupMenu(self, evt=None):
        menu = wx.Menu()
        menu.Append(self.TBMENU_NEXT, 'Next')
        menu.Append(self.TBMENU_PREVIOUS, 'Previous')
        menu.AppendSeparator()
        menu.Append(self.TBMENU_RANK_5, 'Rank 5')
        menu.Append(self.TBMENU_RANK_4, 'Rank 4')
        menu.Append(self.TBMENU_RANK_3, 'Rank 3')
        menu.Append(self.TBMENU_RANK_2, 'Rank 2')
        menu.Append(self.TBMENU_RANK_1, 'Rank 1')
        menu.Append(self.TBMENU_RANK_0, 'Rank 0')
        menu.AppendSeparator()
        menu.Append(self.TBMENU_CLOSE, 'Exit')
        return menu

    def OnNext(self, evt):
        logging.info('Fetching a wallpaper...')
        image = self.wallhaven.fetch_one()
        self.wallhaven.set_wallpaper(image)
        logging.info('{} has been set as wallpaper.'.format(image))

    def OnTaskBarClose(self, evt):
        self.frame.Close()

    def OnTaskBarLeftClick(self, evt):
        menu = self.CreatePopupMenu()
        self.PopupMenu(menu)
        menu.Destroy()


class TrayFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, 'iWallpaper')
        self.tbIcon = TrayIcon(self)
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def onClose(self, evt):
        self.tbIcon.RemoveIcon()
        self.tbIcon.Destroy()
        self.Destroy()
