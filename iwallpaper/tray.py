import wx
import wx.adv
import os.path as path

import iwallpaper.image_server as image_server


class TrayIcon(wx.adv.TaskBarIcon):
    TBMENU_CURRENT = wx.NewId()
    TBMENU_NEXT = wx.NewId()
    TBMENU_PREVIOUS = wx.NewId()
    TBMENU_DELETE = wx.NewId()
    TBMENU_RANK_5 = wx.NewId()
    TBMENU_RANK_4 = wx.NewId()
    TBMENU_RANK_3 = wx.NewId()
    TBMENU_RANK_2 = wx.NewId()
    TBMENU_RANK_1 = wx.NewId()
    TBMENU_CLOSE = wx.NewId()

    def __init__(self, frame, daemon):
        wx.adv.TaskBarIcon.__init__(self)
        self.frame = frame
        self.daemon = daemon
        self.daemon.next_image()
        self.__enable_menu_previous = True
        self.__enable_menu_rank = True

        img = wx.Image('{}/favicon.ico'.format(
            path.dirname(path.realpath(__file__))), wx.BITMAP_TYPE_ANY)
        bmp = wx.Bitmap(img)
        self.icon = wx.Icon()
        self.icon.CopyFromBitmap(bmp)
        self.SetIcon(self.icon, 'iWallpaper')
        self.Bind(wx.EVT_MENU, self.OnNext, id=self.TBMENU_NEXT)
        self.Bind(wx.EVT_MENU, self.OnPrevious, id=self.TBMENU_PREVIOUS)
        self.Bind(wx.EVT_MENU, self.OnDelete, id=self.TBMENU_DELETE)
        self.Bind(wx.EVT_MENU, self.OnRank5, id=self.TBMENU_RANK_5)
        self.Bind(wx.EVT_MENU, self.OnRank4, id=self.TBMENU_RANK_4)
        self.Bind(wx.EVT_MENU, self.OnRank3, id=self.TBMENU_RANK_3)
        self.Bind(wx.EVT_MENU, self.OnRank2, id=self.TBMENU_RANK_2)
        self.Bind(wx.EVT_MENU, self.OnRank1, id=self.TBMENU_RANK_1)
        self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=self.TBMENU_CLOSE)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.OnTaskBarLeftClick)

        self.wallhaven = image_server.Wallhaven()

    def CreatePopupMenu(self, evt=None):
        menu = wx.Menu()
        menu.Append(self.TBMENU_CURRENT, self.__get_menu_current_label())
        menu.Enable(self.TBMENU_CURRENT, False)
        menu.Append(self.TBMENU_NEXT, 'Next')
        menu.Append(self.TBMENU_PREVIOUS, 'Previous')
        menu.Enable(self.TBMENU_PREVIOUS, self.__enable_menu_previous)
        menu.Append(self.TBMENU_DELETE, 'Delete')
        menu.AppendSeparator()
        menu.Append(self.TBMENU_RANK_5, 'Rank as 5 stars')
        menu.Enable(self.TBMENU_RANK_5, self.__enable_menu_rank)
        menu.Append(self.TBMENU_RANK_4, 'Rank as 4 stars')
        menu.Enable(self.TBMENU_RANK_4, self.__enable_menu_rank)
        menu.Append(self.TBMENU_RANK_3, 'Rank as 3 stars')
        menu.Enable(self.TBMENU_RANK_3, self.__enable_menu_rank)
        menu.Append(self.TBMENU_RANK_2, 'Rank as 2 stars')
        menu.Enable(self.TBMENU_RANK_2, self.__enable_menu_rank)
        menu.Append(self.TBMENU_RANK_1, 'Rank as 1 star')
        menu.Enable(self.TBMENU_RANK_1, self.__enable_menu_rank)
        menu.AppendSeparator()
        menu.Append(self.TBMENU_CLOSE, 'Exit')
        self.menu = menu
        return menu

    def OnNext(self, evt):
        self.daemon.next_image()
        if self.__enable_menu_previous is False:
            self.__enable_menu_previous = True
        if self.__enable_menu_rank is False:
            self.__enable_menu_rank = True

    def __get_menu_current_label(self):
        if self.daemon.image is None:
            return 'Current: None'

        return 'Current {}/{}/{}'.format(self.daemon.image.hashsum[0:4],
                                         self.daemon.predict_rank,
                                         self.daemon.image.rank)

    def OnPrevious(self, evt):
        if self.daemon.previous_image() is None:
            self.__enable_menu_previous = False

    def OnDelete(self, evt):
        self.daemon.delete_image()

    def OnRank5(self, evt):
        if self.daemon.rank_image(5) is None:
            self.__enable_menu_rank = False

    def OnRank4(self, evt):
        if self.daemon.rank_image(4) is None:
            self.__enable_menu_rank = False

    def OnRank3(self, evt):
        if self.daemon.rank_image(3) is None:
            self.__enable_menu_rank = False

    def OnRank2(self, evt):
        if self.daemon.rank_image(2) is None:
            self.__enable_menu_rank = False

    def OnRank1(self, evt):
        if self.daemon.rank_image(1) is None:
            self.__enable_menu_rank = False

    def OnTaskBarClose(self, evt):
        self.frame.Close()

    def OnTaskBarLeftClick(self, evt):
        menu = self.CreatePopupMenu()
        self.PopupMenu(menu)
        menu.Destroy()


class TrayFrame(wx.Frame):
    def __init__(self, daemon):
        wx.Frame.__init__(self, None, wx.ID_ANY, 'iWallpaper')
        self.tbIcon = TrayIcon(self, daemon)
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def onClose(self, evt):
        self.tbIcon.RemoveIcon()
        self.tbIcon.Destroy()
        self.Destroy()
