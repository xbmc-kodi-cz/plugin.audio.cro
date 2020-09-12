# -*- coding: utf-8 -*-
import os                     
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc

from libs.utils import call_api
from libs.favourites import get_favourites, set_listened

_url = sys.argv[0]
_handle = int(sys.argv[1])

def play(url, showId, episodeId):
    favourites = get_favourites(others = 0)
    if showId in favourites:
        set_listened(episodeId, showId)
    list_item = xbmcgui.ListItem(path = url)
    list_item.setContentLookup(False)
    xbmcplugin.setResolvedUrl(_handle, True, list_item)

def play_live(url, title, img):
    list_item = xbmcgui.ListItem(label = title, path = url)
    if img != None:
        list_item.setArt({ "thumb" : img, "icon" : img })
    xbmcplugin.setResolvedUrl(_handle, True, list_item)
    playlist=xbmc.PlayList(1)
    playlist.clear()
    xbmc.PlayList(1).add(url, list_item)
    xbmc.Player().play(playlist)