# -*- coding: utf-8 -*-
import os                     
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc

from urllib import quote, unquote_plus
from urlparse import parse_qsl

from libs.utils import get_url, call_api, parse_date
from libs.stations import get_stations, get_station_from_stationId
from libs.persons import get_person

_url = sys.argv[0]
_handle = int(sys.argv[1])
addon = xbmcaddon.Addon(id='plugin.audio.cro')

def list_shows_menu(label):
    list_item = xbmcgui.ListItem(label="Stanice")
    url = get_url(action='list_shows_stations', label = "Stanice")  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle)

def list_shows_stations(label):
    xbmcplugin.setPluginCategory(_handle, label)   
    stations, stations_nums  = get_stations(filtered=1)
    for num in sorted(stations_nums.keys()):
        list_item = xbmcgui.ListItem(label=stations[stations_nums[num]]["title"])
        url = get_url(action='list_shows_stations_shows', stationId =  stations[stations_nums[num]]["id"], page = 1, label = stations[stations_nums[num]]["title"].encode("utf-8"))  
        list_item.setArt({ "thumb" : stations[stations_nums[num]]["img"], "icon" : stations[stations_nums[num]]["img"] })
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle)        

def list_shows_stations_shows(stationId, page, label):
    xbmcplugin.setPluginCategory(_handle, label)   
    page = int(page)
    page_size = 30
    station  = get_station_from_stationId(stationId)
    data = call_api(url = "https://api.mujrozhlas.cz/stations/" + stationId + "/shows?page[limit]=" + str(page_size) +  "&page[offset]=" + str((page-1)*page_size))
    if "err" in data:
        xbmcgui.Dialog().notification("ČRo","Problém při získání pořadů", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()
    if "data" in data and len(data["data"]) > 0:
        items_count = int(data["meta"]["count"])
        for show in data["data"]:
            cast = [] 
            list_item = xbmcgui.ListItem(label=show["attributes"]["title"])
            list_item.setArt({ "thumb" : show["attributes"]["asset"]["url"], "icon" : show["attributes"]["asset"]["url"] })
            list_item.setInfo( "video", { "title" : show["attributes"]["title"], "director" : [show["attributes"]["asset"]["credit"]["author"]] , "plot" : show["attributes"]["description"], "studio" : station  })            
            if "participants" in show["relationships"] and len(show["relationships"]["participants"]["data"]) > 0:
                for person in show["relationships"]["participants"]["data"]:
                    cast.append(get_person(person["id"]))
                list_item.setInfo( "video", { "cast" : cast })            
            url = get_url(action='list_show', showId = show["id"], page = 1, label = show["attributes"]["title"].encode("utf-8"))  
            menus = [("Přidat k oblíbeným pořadům", "RunPlugin(plugin://plugin.audio.cro?action=add_favourites&showId=" + str(show["id"]) + "&others=0)"),
                     ("Přidat k ostatním obl. pořadům", "RunPlugin(plugin://plugin.audio.cro?action=add_favourites&showId=" + str(show["id"]) + "&others=1)")
                    ]
            list_item.addContextMenuItems(menus)
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)        
        if page * page_size <= items_count:
            list_item = xbmcgui.ListItem(label="Následující strana")
            url = get_url(action='list_shows_stations_shows', stationId =  stationId, page = page + 1, label = label)  
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
        xbmcplugin.endOfDirectory(_handle)        
    else:
        xbmcgui.Dialog().notification("ČRo","Nenalezen žádný pořad", xbmcgui.NOTIFICATION_WARNING, 4000)
        sys.exit()

def list_show(showId, page, label, mark_new = 0):
    page = int(page)
    page_size = 30
    show = get_show(showId)
    xbmcplugin.setPluginCategory(_handle, label)    
    data = call_api(url = "https://api.mujrozhlas.cz/shows/" + showId + "/episodes?sort=-since&page[limit]=" + str(page_size) + "&page[offset]=" + str((page-1)*page_size))
    if "err" in data:
        xbmcgui.Dialog().notification("ČRo","Problém při získání pořadů", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()
    if "data" in data and len(data["data"]) > 0:
        items_count = int(data["meta"]["count"])
        for episode in data["data"]:
            if "attributes" in episode and "title" in episode["attributes"] and len(episode["attributes"]["title"]) > 0:
                starttime =  parse_date(episode["attributes"]["since"])
                if "mirroredSerial" in episode["attributes"] and "totalParts" in episode["attributes"]["mirroredSerial"] and "part" in episode["attributes"]:
                    parts =  " (" + str(episode["attributes"]["part"]) + "/" + str(episode["attributes"]["mirroredSerial"]["totalParts"]) + ") "
                else:
                    parts = ""      
                title = episode["attributes"]["title"] + parts + " (" + starttime.strftime("%d.%m.%Y %H:%M") + ")"
                from libs.favourites import get_listened
                link = episode["attributes"]["audioLinks"][0]["url"]
                if int(mark_new) == 1 and not get_listened(episode["id"]):
                    list_item = xbmcgui.ListItem(label="* " + title)
                else:
                    list_item = xbmcgui.ListItem(label=title)                    
                list_item.setArt({ "thumb" : show["img"], "icon" : show["img"] })
                list_item.setInfo( "video", { "tvshowtitle" : show["title"], "title" : title, "aired" : starttime.strftime("%Y-%m-%d"), "director" : [show["director"]] , "plot" : show["description"], "studio" : show["station"] })
                if len(show["cast"]) > 0:
                    list_item.setInfo( "video", { "cast" : show["cast"] })                
                list_item.setProperty("IsPlayable", "true")
                list_item.setContentLookup(False)
                url = get_url(action='play', url = link.encode("utf-8"), showId = showId, episodeId = episode["id"])  
                xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
        if page * page_size <= items_count:
            list_item = xbmcgui.ListItem(label="Následující strana")
            url = get_url(action='list_show', showId =  showId, page = page + 1, label = label, mark_new = mark_new)  
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

        xbmcplugin.endOfDirectory(_handle, cacheToDisc = False)
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
        cast = []
        if "participants" in data["data"]["relationships"] and len(data["data"]["relationships"]["participants"]["data"]) > 0:
            for person in data["data"]["relationships"]["participants"]["data"]:
                    cast.append(get_person(person["id"]))

        if len(data["data"]["relationships"]["stations"]["data"]) > 0:
            station  = get_station_from_stationId(data["data"]["relationships"]["stations"]["data"][0]["id"])
        else:
            station = ""
        return { "id" : showId, "title" : title, "img" : img, "description" : description, "shortDescription" : shortDescription, "director" : author, "source" : source, "cast" : cast, "station" : station }
    else:
        xbmcgui.Dialog().notification("ČRo","Problém při získání dat o pořadu", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()    

