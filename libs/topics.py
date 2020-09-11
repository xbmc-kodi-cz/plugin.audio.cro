# -*- coding: utf-8 -*-
import os                     
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc

from datetime import datetime

from libs.utils import get_url, call_api, parse_date
from libs.shows import get_show

_url = sys.argv[0]
_handle = int(sys.argv[1])
addon = xbmcaddon.Addon(id='plugin.audio.cro')

def list_topics(label):
    xbmcplugin.setPluginCategory(_handle, label)    
    data = call_api(url = "https://api.mujrozhlas.cz/topics")
    if "err" in data:
        xbmcgui.Dialog().notification("ČRo","Problém při získání seznamu témat", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()
    if "data" in data and len(data["data"]) > 0:
        for topic in data["data"]:
            if "attributes" in topic and "title" in topic["attributes"] and len(topic["attributes"]["title"]) > 0:
                topicId = topic["id"]
                list_item = xbmcgui.ListItem(label=topic["attributes"]["title"])
                url = get_url(action='list_topic', topicId = topicId, label = label + " / " + topic["attributes"]["title"].encode("utf-8"))  
                list_item.setArt({ "thumb" : topic["attributes"]["asset"]["url"], "icon" : topic["attributes"]["asset"]["url"]})
                xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
        xbmcplugin.endOfDirectory(_handle)
    else:
        xbmcgui.Dialog().notification("ČRo","Problém při získání seznamu témat", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()

def list_topic(topicId, label):
    xbmcplugin.setPluginCategory(_handle, label)    
    data = call_api(url = "https://api.mujrozhlas.cz/topics/" + topicId + "/episodes?page[limit]=100")
    if "err" in data:
        xbmcgui.Dialog().notification("ČRo","Problém při získání pořadů", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()
    if "data" in data and len(data["data"]) > 0:
        widgets = get_widgets(topicId)
        for widget in widgets:
            list_item = xbmcgui.ListItem(label=widget)
            list_item.setProperty("IsPlayable", "false")
            url = get_url(action='list_topic_recommended', topicId = topicId, filtr = widget.encode("utf-8"),  label = label + " / " + widget.encode("utf-8"))  
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

        shows = {}
        shows_added = []
        for episode in data["data"]:
            if "attributes" in episode and "title" in episode["attributes"] and len(episode["attributes"]["title"]) > 0:
                if episode["relationships"]["show"]["data"]["id"] not in shows_added:
                    show = get_show(episode["relationships"]["show"]["data"]["id"])
                    shows.update({ show["title"] : show })
                    shows_added.append(show["id"])
        for key in sorted(shows.keys()):      
                show = shows[key] 
                list_item = xbmcgui.ListItem(label=show["title"])
                list_item.setArt({ "thumb" : show["img"], "icon" : show["img"] })
                list_item.setInfo( "video", { "title" : show["title"], "director" : [show["director"]], "plot" : show["description"], "studio" : show["station"] })
                if len(show["cast"]) > 0:
                    list_item.setInfo( "video", { "cast" : show["cast"] })   
                menus = [("Přidat k oblíbeným pořadům", "RunPlugin(plugin://plugin.audio.cro?action=add_favourites&showId=" + str(show["id"]) + "&others=0)"),
                         ("Přidat k ostatním obl. pořadům", "RunPlugin(plugin://plugin.audio.cro?action=add_favourites&showId=" + str(show["id"]) + "&others=1)")
                        ]
                list_item.addContextMenuItems(menus)
                url = get_url(action='list_show', showId = show["id"], page = 1, label = show["title"].encode("utf-8"))                
                list_item.setContentLookup(False) 
                xbmcplugin.addDirectoryItem(_handle, url, list_item, True)              
        xbmcplugin.endOfDirectory(_handle)
    else:
        xbmcgui.Dialog().notification("ČRo","Problém při získání pořadů", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()

def list_topic_recommended(topicId, filtr, label):
    xbmcplugin.setPluginCategory(_handle, label)    
    data = call_api(url = "https://api.mujrozhlas.cz/topics/" + topicId)
    if "err" in data:
        xbmcgui.Dialog().notification("ČRo","Problém při získání pořadů", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()
    if "data" in data and len(data["data"]) > 0 and "attributes" in data["data"] and "widgets" in data["data"]["attributes"]:
        for widget in data["data"]["attributes"]["widgets"]:
            if "attributes" in widget and "title" in widget["attributes"] and widget["attributes"]["title"].encode("utf-8") == filtr:
                if "items" in widget["attributes"]:
                    items = widget["attributes"]["items"]
                elif "entities" in widget["attributes"]:
                    items = widget["attributes"]["entities"]
                for item in items:
                    if "entity" in item and "type" in item["entity"]:
                        if item["entity"]["type"] == "show":
                            show = get_show(item["entity"]["id"])
                            list_item = xbmcgui.ListItem(label=show["title"])
                            list_item.setArt({ "thumb" : show["img"], "icon" : show["img"] })
                            list_item.setInfo( "video", { "title" : show["title"], "director" : [show["director"]] , "plot" : show["description"], "studio" : show["station"] })
                            if len(show["cast"]) > 0:
                                list_item.setInfo( "video", { "cast" : show["cast"] })                
                            menus = [("Přidat k oblíbeným pořadům", "RunPlugin(plugin://plugin.audio.cro?action=add_favourites&showId=" + str(show["id"]) + "&others=0)"),
                                     ("Přidat k ostatním obl. pořadům", "RunPlugin(plugin://plugin.audio.cro?action=add_favourites&showId=" + str(show["id"]) + "&others=1)")
                                    ]
                            list_item.addContextMenuItems(menus)
                            url = get_url(action='list_show', showId = show["id"], page = 1, label = show["title"].encode("utf-8"))  
                            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)                                
                        if item["entity"]["type"] == "episode":
                            starttime =  parse_date(item["entity"]["attributes"]["since"])
                            title = item["entity"]["attributes"]["mirroredShow"]["title"] + " - " + item["entity"]["attributes"]["title"] + " (" + starttime.strftime("%d.%m.%Y %H:%M") + ")"
                            url = item["entity"]["attributes"]["audioLinks"][0]["url"]
                            list_item = xbmcgui.ListItem(label=title)
                            list_item.setProperty("IsPlayable", "true")
                            list_item.setContentLookup(False)
                            url = get_url(action='play', url = url)  
                            xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
                    if "type" in item and item["type"] == "episode":
                        starttime =  parse_date(item["attributes"]["since"])
                        title = item["attributes"]["mirroredShow"]["title"] + " - " + item["attributes"]["title"] + " (" + starttime.strftime("%d.%m.%Y %H:%M") + ")"
                        url = item["attributes"]["audioLinks"][0]["url"]
                        list_item = xbmcgui.ListItem(label=title)
                        list_item.setProperty("IsPlayable", "true")
                        list_item.setContentLookup(False)
                        url = get_url(action='play', url = url)  
                        xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
        xbmcplugin.endOfDirectory(_handle)
    else:
        xbmcgui.Dialog().notification("ČRo","Problém při získání pořadů", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()

def get_widgets(topicId):
    widgets = []
    data = call_api(url = "https://api.mujrozhlas.cz/topics/" + topicId)
    if "err" in data:
        xbmcgui.Dialog().notification("ČRo","Problém při získání pořadů", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()
    if "data" in data and len(data["data"]) > 0 and "attributes" in data["data"] and "widgets" in data["data"]["attributes"]:
        for widget in data["data"]["attributes"]["widgets"]:
            if "title" in widget["attributes"] and len(widget["attributes"]["title"]) > 0:
                widgets.append(widget["attributes"]["title"])
    return widgets
