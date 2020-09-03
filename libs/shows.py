# -*- coding: utf-8 -*-
import os                     
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc

from libs.utils import get_url, call_api, parse_date

_url = sys.argv[0]
_handle = int(sys.argv[1])
addon = xbmcaddon.Addon(id='plugin.audio.cro')

def list_shows(showId, label):
    xbmcplugin.setPluginCategory(_handle, label)    
    data = call_api(url = "https://api.mujrozhlas.cz/shows/" + showId + "/episodes?sort=-since")
    if "err" in data:
        xbmcgui.Dialog().notification("ČRo","Problém při získání pořadů", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()
    if "data" in data and len(data["data"]) > 0:
        for episode in data["data"]:
            if "attributes" in episode and "title" in episode["attributes"] and len(episode["attributes"]["title"]) > 0:
                starttime =  parse_date(episode["attributes"]["since"])
                title = episode["attributes"]["title"] + " (" + starttime.strftime("%d.%m.%Y %H:%M") + ")"
                url = episode["attributes"]["audioLinks"][0]["url"]
                list_item = xbmcgui.ListItem(label=title)
                list_item.setProperty("IsPlayable", "true")
                list_item.setContentLookup(False)
                url = get_url(action='play', url = url)  
                xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
        xbmcplugin.endOfDirectory(_handle)
    else:
        xbmcgui.Dialog().notification("ČRo","Problém při získání pořadů", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()

def get_show(showId):
    data = call_api(url = "https://api.mujrozhlas.cz/shows/" + showId)
    if "err" in data:
        xbmcgui.Dialog().notification("ČRo","Problém při získání dat o pořadu", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()
    if "data" in data and len(data["data"]) > 0 and "attributes" in data["data"]:
        title = data["data"]["attributes"]["title"]
        img = data["data"]["attributes"]["asset"]["url"]                
        description = data["data"]["attributes"]["description"]
        shortDescription = data["data"]["attributes"]["shortDescription"]
        author = data["data"]["attributes"]["asset"]["credit"]["author"]
        source = data["data"]["attributes"]["asset"]["credit"]["source"]
        return { "id" : showId, "title" : title, "img" : img, "description" : description, "shortDescription" : shortDescription, "author" : author, "source" : source }
    else:
        xbmcgui.Dialog().notification("ČRo","Problém při získání dat o pořadu", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()    
