# -*- coding: utf-8 -*-
import os                     
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc

_url = sys.argv[0]
_handle = int(sys.argv[1])

def play(url):
    list_item = xbmcgui.ListItem(path = url)
    list_item.setContentLookup(False)
    xbmcplugin.setResolvedUrl(_handle, True, list_item)
