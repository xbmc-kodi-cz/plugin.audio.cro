# -*- coding: utf-8 -*-
import os                     
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc

from urlparse import parse_qsl

from libs.utils import get_url, call_api
from libs.topics import list_topics, list_topic, list_topic_recommended
from libs.shows import list_shows
from libs.search import list_search, do_search
from libs.player import play

_url = sys.argv[0]
_handle = int(sys.argv[1])
addon = xbmcaddon.Addon(id='plugin.audio.cro')

def list_menu():
    # list_item = xbmcgui.ListItem(label="Archiv pořadů")
    # url = get_url(action='list_archiv', label = "Archiv pořadů")  
    # xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    list_item = xbmcgui.ListItem(label="Témata")
    url = get_url(action='list_topics', label = "Témata")  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    list_item = xbmcgui.ListItem(label="Vyhledávání")
    url = get_url(action='list_search', label = "Vyhledávání")  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    xbmcplugin.endOfDirectory(_handle)

def list_archiv(label):
    xbmcplugin.setPluginCategory(_handle, label)    
    data = call_api(url = "https://api.mujrozhlas.cz/stations")
    if "err" in data:
        xbmcgui.Dialog().notification("ČRo","Problém při získání seznamu stanic", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()
    if "data" in data and len(data["data"]) > 0:
        for station in data["data"]:
            if "attributes" in station and "shortTitle" in station["attributes"] and len(station["attributes"]["shortTitle"]) > 0:
                stationId = station["id"]
                list_item = xbmcgui.ListItem(label=station["attributes"]["shortTitle"])
                url = get_url(action='list_arch_days', stationId = stationId, label = label + station["attributes"]["shortTitle"].encode("utf-8"))  
                xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
        xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)
    else:
        xbmcgui.Dialog().notification("ČRo","Problém při získání seznamu stanic", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()

def router(paramstring):
    params = dict(parse_qsl(paramstring))
    if params:
        if params["action"] == "list_archiv":
            list_archiv(params["label"])

        elif params['action'] == 'list_topics':
            list_topics(params["label"]) 
        elif params['action'] == 'list_topic':
            list_topic(params["topicId"], params["label"])             
        elif params['action'] == 'list_topic_recommended':
            list_topic_recommended(params["topicId"], params["filtr"], params["label"])             

        elif params['action'] == 'list_shows':
            list_shows(params["showId"], params["label"])   

        elif params['action'] == 'list_search':
            list_search(params["label"])
        elif params['action'] == 'do_search':
            do_search(params["query"], params["label"])

        elif params['action'] == 'play':
            play(params["url"])

        else:
            raise ValueError('Neznámý parametr: {0}!'.format(paramstring))
    else:
        list_menu()

if __name__ == '__main__':
    router(sys.argv[2][1:])
