# -*- coding: utf-8 -*-
import os                     
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc

import codecs
import json
import time

from libs.utils import call_api, get_url

_url = sys.argv[0]
_handle = int(sys.argv[1])

addon = xbmcaddon.Addon(id='plugin.audio.cro')
addon_userdata_dir = xbmc.translatePath(addon.getAddonInfo('profile'))

def get_stations(filtered = 1):
    stations = {}
    stations_nums = {}
    max_num = 0

    not_found = 0
    valid_to = -1
    filename = addon_userdata_dir + "stations.txt"
    try:
      with codecs.open(filename, "r", encoding="utf-8") as file:
        for line in file:
          item = line[:-1]
          data = json.loads(item)
          stations = data["stations"]
          stations_nums_str = data["stations_nums"]
          for num in stations_nums_str.keys():
              stations_nums.update({ int(num) : stations_nums_str[num] })
          valid_to = data["valid_to"]
    except IOError:
      not_found = 1
    max_num = len(stations_nums)
    if not_found == 1 or valid_to < int(time.time()):
        data = call_api(url = "https://api.mujrozhlas.cz/stations")
        if "err" in data:
            xbmcgui.Dialog().notification("ČRo","Problém při načtení stanic", xbmcgui.NOTIFICATION_ERROR, 4000)
            sys.exit()
        if "data" in data and len(data["data"]) > 0:
            for station in data["data"]:
                if station["attributes"]["shortTitle"] not in stations.keys():
                    max_num = max_num + 1        
                    stations_nums.update({ max_num : station["attributes"]["shortTitle"] })
                    if "url" in station["attributes"]["asset"]:
                        img = station["attributes"]["asset"]["url"]
                    else:
                        img = ""    
                    stations.update({ station["attributes"]["shortTitle"] : { "id" : station["id"], "title" : station["attributes"]["shortTitle"], "img" : img, "enabled" : 1 }})
            try:
                with codecs.open(filename, "w", encoding="utf-8") as file:
                    data = json.dumps({"stations" : stations, "stations_nums" : stations_nums,"valid_to" : int(time.time()) + 60*60*24})
                    file.write('%s\n' % data)
            except IOError:
                xbmcgui.Dialog().notification("ČRo","Problém při uložení stanic", xbmcgui.NOTIFICATION_ERROR, 4000)
        else:
            xbmcgui.Dialog().notification("ČRo","Problém při načtení stanic", xbmcgui.NOTIFICATION_ERROR, 4000)
            sys.exit()
    if int(filtered) == 1:
        for num in sorted(stations_nums.keys()):
            if int(stations[stations_nums[num]]["enabled"]) == 0:
                del stations[stations_nums[num]]
                del stations_nums[num]
    return stations, stations_nums     
    
def toogle_station(stationId):
    filename = addon_userdata_dir + "stations.txt"
    stations, stations_nums  = get_stations(filtered=0)
    for key in stations:
        if stations[key]["id"] == stationId:
            if int(stations[key]["enabled"]) == 1:
               stations[key]["enabled"] = 0
            else:
               stations[key]["enabled"] = 1
    try:
        with codecs.open(filename, "w", encoding="utf-8") as file:
            data = json.dumps({"stations" : stations, "stations_nums" : stations_nums,"valid_to" : int(time.time()) + 60*60*24})
            file.write('%s\n' % data)
    except IOError:
        xbmcgui.Dialog().notification("ČRo","Problém při uložení stanic", xbmcgui.NOTIFICATION_ERROR, 4000)
    xbmc.executebuiltin('Container.Refresh')

def list_stations(label):
    xbmcplugin.setPluginCategory(_handle, label)     
    stations, stations_nums  = get_stations(filtered=0)
    for num in sorted(stations_nums.keys()):
        if int(stations[stations_nums[num]]["enabled"]) == 0:
            list_item = xbmcgui.ListItem(label="[COLOR red]" + stations[stations_nums[num]]["title"] + "[/COLOR]")
        else:  
            list_item = xbmcgui.ListItem(label=stations[stations_nums[num]]["title"])
        url = get_url(action='toogle_station', stationId =  stations[stations_nums[num]]["id"])  
        list_item.setArt({ "thumb" : stations[stations_nums[num]]["img"], "icon" : stations[stations_nums[num]]["img"] })
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle)        

def get_station_from_stationId(stationId):
    stations, stations_nums  = get_stations(filtered=0)
    for num in sorted(stations_nums.keys()):
        if stations[stations_nums[num]]["id"] == stationId:
            return stations_nums[num]