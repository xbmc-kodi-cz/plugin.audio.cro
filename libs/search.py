# -*- coding: utf-8 -*-
import os                     
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc

try:
    from xbmcvfs import translatePath
except ImportError:
    from xbmc import translatePath

try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote

from libs.utils import call_api, get_url, encode
from libs.shows import get_show, get_person, list_show

_url = sys.argv[0]
_handle = int(sys.argv[1])

addon = xbmcaddon.Addon(id='plugin.audio.cro')
addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))

def list_search(label):
    list_item = xbmcgui.ListItem(label="Podle názvu")
    url = get_url(action='list_search_title', label = "Vyhledávání podle názvu")  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    list_item = xbmcgui.ListItem(label="Podle osoby")
    url = get_url(action='list_search_person', label = "Vyhledávání podle osoby")  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle)    

def list_search_title(label):    
    xbmcplugin.setPluginCategory(_handle, label)
    list_item = xbmcgui.ListItem(label="Nové hledání")
    url = get_url(action='do_search', query = "-----", label = label + " / " + "Nové hledání")
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    history = load_search_history()
    for item in history:
        list_item = xbmcgui.ListItem(label=item)
        url = get_url(action='do_search', query = item, label = label + " / " + item)
        list_item.addContextMenuItems([("Smazat", "RunPlugin(plugin://plugin.audio.cro?action=delete_search&query=" + quote(item) + ")")])
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle,cacheToDisc = False)


def list_search_person(label):    
    xbmcplugin.setPluginCategory(_handle, label)
    list_item = xbmcgui.ListItem(label="Nové hledání")
    url = get_url(action='do_search', query = "-----", label = label + " / " + "Nové hledání")
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    history = load_search_history_person()
    for item in history:
        list_item = xbmcgui.ListItem(label=item)
        url = get_url(action='do_search_person', query = item, label = label + " / " + item)
        list_item.addContextMenuItems([("Smazat", "RunPlugin(plugin://plugin.audio.cro?action=delete_search_person&query=" + quote(item) + ")")])
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle,cacheToDisc = False)    

def do_search_person(query, label):
    pass

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
    shows_ordered = {}
    
    shows, shows_ordered = search_episodes(shows, shows_ordered, "title", query)
    #shows, shows_ordered = search_episodes(shows, shows_ordered, "description", query)
    shows, shows_ordered = search_shows(shows, shows_ordered, "title", query)
    #shows, shows_ordered = search_shows(shows, shows_ordered, "description", query)

    if len(shows) > 0:
        for key in sorted(shows_ordered, key=shows.get('id')):             
                show = shows[key] 
                list_item = xbmcgui.ListItem(label=show["title"])
                list_item.setArt({ "thumb" : show["img"], "icon" : show["img"] })
                list_item.setInfo( "video", { "title" : show["title"], "director" : [show["director"]] , "plot" : show["description"], "studio" : show["station"] })
                if len(show["cast"]) > 0:
                    list_item.setInfo( "video", { "cast" : show["cast"] })                
                menus = [("Přidat k oblíbeným pořadům", "RunPlugin(plugin://plugin.audio.cro?action=add_favourites&showId=" + str(show["id"]) + "&others=0)"),
                         ("Přidat k ostatním obl. pořadům", "RunPlugin(plugin://plugin.audio.cro?action=add_favourites&showId=" + str(show["id"]) + "&others=1)")
                        ]
                list_item.addContextMenuItems(menus)
                url = get_url(action='list_show', showId = show["id"], page = 1, label = encode(show["title"]))  
                xbmcplugin.addDirectoryItem(_handle, url, list_item, True)              
    else:
        xbmcgui.Dialog().notification("ČRo","Nic nebylo nalezeno", xbmcgui.NOTIFICATION_WARNING, 4000)
    xbmcplugin.endOfDirectory(_handle)

def delete_search(query):
    filename = addon_userdata_dir + "search_history.txt"
    history = load_search_history()
    for item in history:
        if item == query:
            history.remove(item)
    try:
        with open(filename, "w") as file:
            for item in history:
                file.write('%s\n' % item)
    except IOError:
        pass
    xbmc.executebuiltin('Container.Refresh')

def delete_search_person(query):
    filename = addon_userdata_dir + "search_history_person.txt"
    history = load_search_history_person()
    for item in history:
        if item == query:
            history.remove(item)
    try:
        with open(filename, "w") as file:
            for item in history:
                file.write('%s\n' % item)
    except IOError:
        pass
    xbmc.executebuiltin('Container.Refresh')    

def search_episodes(shows, shows_ordered, attribute, query):
    data = call_api(url = "https://api.mujrozhlas.cz/episodes?filter[" + attribute + "][like]=" + quote(query) + "&page[limit]=100")
    if "err" not in data and "data" in data and len(data["data"]) > 0:
        for item in data["data"]:
            if item["type"] == "episode" or item["type"] == "serial":
                if item["relationships"]["show"]["data"]["id"] not in shows.keys() and ("audioLinks" not in item["attributes"] or len(item["attributes"]["audioLinks"]) > 0):
                    show = get_show(item["relationships"]["show"]["data"]["id"])
                    shows.update({ show["id"] : show })
                    shows_ordered.update({ show["id"] : show["title"] })
            if item["type"] == "show":
                if item["id"] not in shows.keys():
                    show = get_show(item["id"])
                    shows.update({ show["id"] : show })
                    shows_ordered.update({ show["id"] : show["title"] })
    return shows, shows_ordered                

def search_shows(shows, shows_ordered, attribute, query):
    data = call_api(url = "https://api.mujrozhlas.cz/shows?filter[" + attribute + "][like]=" + quote(query) + "&page[limit]=100")
    if "err" not in data and "data" in data and len(data["data"]) > 0:
        for item in data["data"]:
            if item["id"] not in shows.keys():
                show = get_show(item["id"])
                shows.update({ show["id"] : show })
                shows_ordered.update({ show["id"] : show["title"] })
    return shows, shows_ordered                

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

def save_search_history_person(query):
    max_history = int(addon.getSetting("search_history"))
    cnt = 0
    history = []
    filename = addon_userdata_dir + "search_history_person.txt"
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

def load_search_history_person():
    history = []
    filename = addon_userdata_dir + "search_history_person.txt"
    try:
        with open(filename, "r") as file:
            for line in file:
                item = line[:-1]
                history.append(item)
    except IOError:
        history = []
    return history    
