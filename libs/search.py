# -*- coding: utf-8 -*-
import os                     
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc

from urllib import quote

from libs.utils import call_api, get_url
from libs.shows import get_show, list_shows

_url = sys.argv[0]
_handle = int(sys.argv[1])

addon = xbmcaddon.Addon(id='plugin.audio.cro')
addon_userdata_dir = xbmc.translatePath(addon.getAddonInfo('profile'))

def list_search(label):
    xbmcplugin.setPluginCategory(_handle, label)
    list_item = xbmcgui.ListItem(label="Nové hledání")
    url = get_url(action='do_search', query = "-----", label = label + " / " + "Nové hledání")
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    history = load_search_history()
    for item in history:
        list_item = xbmcgui.ListItem(label=item)
        url = get_url(action='do_search', query = item, label = label + " / " + item)
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle,cacheToDisc = False)

def do_search(query, label):
    xbmcplugin.setPluginCategory(_handle, label)
    if query == "-----":
      input = xbmc.Keyboard("", "Hledat")
      input.doModal()
      if not input.isConfirmed():
        return
      query = input.getText()
      if len(query) == 0:
        xbmcgui.Dialog().notification("ČRo","Je potřeba zadat vyhledávaný řetězec", xbmcgui.NOTIFICATION_ERROR, 4000)
        return
      else:
        save_search_history(query)

    data = call_api(url = "https://api.mujrozhlas.cz/search?filter[fulltext]=" + quote(query) + "&page[limit]=100")
    if "err" in data:
        xbmcgui.Dialog().notification("ČRo","Problém při vyhledávání", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()
    if "data" in data and len(data["data"]) > 0:
        shows = {}
        shows_added = []
        for item in data["data"]:
            if item["type"] == "episode" or item["type"] == "serial":
                if item["relationships"]["show"]["data"]["id"] not in shows_added:
                    show = get_show(item["relationships"]["show"]["data"]["id"])
                    shows.update({ show["title"] : show })
                    shows_added.append(show["id"])
            if item["type"] == "show":
                if item["id"] not in shows_added:
                    show = get_show(item["id"])
                    shows.update({ show["title"] : show })
                    shows_added.append(show["id"])                

        for key in sorted(shows.keys()):      
                show = shows[key] 
                list_item = xbmcgui.ListItem(label=show["title"])
                list_item.setArt({ "thumb" : show["img"], "icon" : show["img"] })
                list_item.setInfo( "music", { "title" : show["title"], "artist" : show["author"], "comment" : show["description"] })
                url = get_url(action='list_shows', showId = show["id"], label = show["title"].encode("utf-8"))  
                xbmcplugin.addDirectoryItem(_handle, url, list_item, True)              
        xbmcplugin.endOfDirectory(_handle)

    else:
        xbmcgui.Dialog().notification("ČRo","Problém při vyhledávání", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()    


def save_search_history(query):
    max_history = int(addon.getSetting("search_history"))
    cnt = 0
    history = []
    filename = addon_userdata_dir + "search_history.txt"

    try:
      with open(filename, "r") as file:
        for line in file:
          item = line[:-1]
          history.append(item)
    except IOError:
      history = []

    history.insert(0,query)

    with open(filename, "w") as file:
      for item  in history:
        cnt = cnt + 1
        if cnt <= max_history:
            file.write('%s\n' % item)

def load_search_history():
    history = []
    filename = addon_userdata_dir + "search_history.txt"
    try:
      with open(filename, "r") as file:
        for line in file:
          item = line[:-1]
          history.append(item)
    except IOError:
      history = []
    return history
