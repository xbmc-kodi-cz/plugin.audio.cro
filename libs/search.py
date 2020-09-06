# -*- coding: utf-8 -*-
import os                     
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc

from urllib import quote

from libs.utils import call_api, get_url
from libs.shows import get_show, get_person, list_show

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
    shows = {}
    shows_added = []

    shows, shows_added = search_episodes(shows, shows_added, "title", query)
    shows, shows_added = search_episodes(shows, shows_added, "description", query)
    shows, shows_added = search_shows(shows, shows_added, "title", query)
    shows, shows_added = search_shows(shows, shows_added, "description", query)

    if len(shows) > 0:
        for key in sorted(shows.keys()):      
                show = shows[key] 
                list_item = xbmcgui.ListItem(label=show["title"])
                list_item.setArt({ "thumb" : show["img"], "icon" : show["img"] })
                list_item.setInfo( "video", { "title" : show["title"], "director" : [show["author"]] , "plot" : show["description"], "studio" : show["station"] })
                if len(show["cast"]) > 0:
                    list_item.setInfo( "video", { "cast" : show["cast"] })                
                url = get_url(action='list_show', showId = show["id"], label = show["title"].encode("utf-8"))  
                xbmcplugin.addDirectoryItem(_handle, url, list_item, True)              
    else:
        xbmcgui.Dialog().notification("ČRo","Nic nebylo nalezeno", xbmcgui.NOTIFICATION_WARNING, 4000)
    xbmcplugin.endOfDirectory(_handle)

 
def search_episodes(shows, shows_added, attribute, query):
    data = call_api(url = "https://api.mujrozhlas.cz/episodes?filter[" + attribute + "][like]=" + quote(query) + "&page[limit]=100")
    if "err" not in data and "data" in data and len(data["data"]) > 0:
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
    return shows, shows_added                

def search_shows(shows, shows_added, attribute, query):
    data = call_api(url = "https://api.mujrozhlas.cz/shows?filter[" + attribute + "][like]=" + quote(query) + "&page[limit]=100")
    if "err" not in data and "data" in data and len(data["data"]) > 0:
        for item in data["data"]:
            if item["id"] not in shows_added:
                show = get_show(item["id"])
                shows.update({ show["title"] : show })
                shows_added.append(show["id"])
    return shows, shows_added                

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
