# -*- coding: utf-8 -*-
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon

from datetime import datetime, timedelta

from libs.utils import get_url, call_api, parse_date, parse_datetime, encode
from libs.stations import get_stations

_url = sys.argv[0]
_handle = int(sys.argv[1])
addon = xbmcaddon.Addon(id='plugin.audio.cro')

def list_program(label):
    now = datetime.now()
    startDoW = now - timedelta(days=now.weekday())
    endDoW = startDoW + timedelta(days=6)
    xbmcplugin.setPluginCategory(_handle, label) 
    stations, stations_nums  = get_stations(filtered=1)
    for num in sorted(stations_nums.keys()):
        list_item = xbmcgui.ListItem(label=stations[stations_nums[num]]["title"])
        url = get_url(action='list_program_week', stationId = stations[stations_nums[num]]["id"], startdate = startDoW.strftime("%d.%m.%Y"), enddate = endDoW.strftime("%d.%m.%Y"), label = encode(stations[stations_nums[num]]["title"]))  
        list_item.setArt({ "thumb" : stations[stations_nums[num]]["img"], "icon" : stations[stations_nums[num]]["img"] })
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle)      

def list_program_week(stationId, startdate, enddate, label):
    xbmcplugin.setPluginCategory(_handle, label)
    mindate, maxdate = get_minmax_days(stationId)

    startDoW = parse_datetime(startdate) - timedelta(days=7) - timedelta(days= parse_datetime(startdate).weekday())
    endDoW = startDoW + timedelta(days=6)
    if endDoW >= mindate: 
        list_item = xbmcgui.ListItem(label="<<<")
        url = get_url(action='list_program_week', stationId = stationId, startdate = startDoW.strftime("%d.%m.%Y"), enddate = endDoW.strftime("%d.%m.%Y"), label = label)  
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    for i in range (7):
        day = parse_datetime(startdate) + timedelta(days = i)
        if day <= maxdate and day >= mindate:
            if datetime.now().strftime("%d.%m.%Y") == day.strftime("%d.%m.%Y"):
                list_item = xbmcgui.ListItem(label="Dnes")
            else:
                list_item = xbmcgui.ListItem(label=day.strftime("%d.%m.%Y"))
            url = get_url(action='list_program_day', stationId = stationId, day = day.strftime("%d.%m.%Y"), label = label + day.strftime("%d.%m.%Y"))  
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    list_item = xbmcgui.ListItem(label="Přejít na datum")
    url = get_url(action='program_set_week', stationId = stationId, startdate = startdate, enddate = enddate, label = label)  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    startDoW = parse_datetime(startdate) + timedelta(days=7) - timedelta(days=parse_datetime(startdate).weekday())
    endDoW = startDoW + timedelta(days=6)
    if startDoW <= maxdate:
        list_item = xbmcgui.ListItem(label=">>>")
        url = get_url(action='list_program_week', stationId = stationId, startdate = startDoW.strftime("%d.%m.%Y"), enddate = endDoW.strftime("%d.%m.%Y"), label = label)  
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle)      

def list_program_day(stationId, day, label):
    xbmcplugin.setPluginCategory(_handle, label)
    day = parse_datetime(day).strftime("%Y-%m-%d")
    episodeIds = []
    data = call_api(url = "https://api.mujrozhlas.cz/schedule-day-flat?filter[day]=" + day + "&filter[stations.id]=" + stationId)
    if "err" in data:
        xbmcgui.Dialog().notification("ČRo","Problém při načtení programu", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()
    if "data" in data and len(data["data"]) > 0:
        for item in data["data"]:
            episodeIds.append(item["id"])
    else:
        xbmcgui.Dialog().notification("ČRo","Problém při načtení programu", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()

    if len(episodeIds) > 0:
        for episodeId in episodeIds:
            data = call_api(url = "https://api.mujrozhlas.cz/episodes/" + episodeId)
            if "err" not in data and "data" in data and len(data["data"]) > 0:
                for item in data["data"]:
                    print(item)


def program_set_week(stationId, startdate, enddate, label):
    datum = xbmcgui.Dialog().input(heading = "Přejít na datum", type = xbmcgui.INPUT_DATE) 
    if len(datum) > 0: 
        mindate, maxdate = get_minmax_days(stationId)
        datum = parse_datetime(datum)
        startDoW = datum - timedelta(days=datum.weekday())
        endDoW = startDoW + timedelta(days=6)
        if datum >= mindate and datum <= maxdate:         
            startdate = startDoW.strftime("%d.%m.%Y")
            enddate = endDoW.strftime("%d.%m.%Y")
        else:   
            xbmcgui.Dialog().notification("ČRo","Pro zadané datum neexistuje program", xbmcgui.NOTIFICATION_ERROR, 4000)
    list_program_week(stationId = stationId, startdate = startdate, enddate = enddate, label = label)

def get_minmax_days(stationId):
    mindate = ""
    maxdate = ""
    data = call_api(url = "https://api.mujrozhlas.cz/schedule?filter[stations.id]=" + stationId + "&sort=since&page[limit]=1&page[offset]=0")
    if "err" in data:
        xbmcgui.Dialog().notification("ČRo","Problém při načtení programu", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()
    if "data" in data and len(data["data"]) > 0:
        lastitem = int(data["meta"]["count"]) - 1
        for item in data["data"]:
            mindate = parse_date(item["attributes"]["since"]).strftime("%d.%m.%Y")
        data = call_api(url = "https://api.mujrozhlas.cz/schedule?filter[stations.id]=" + stationId + "&sort=since&page[limit]=1&page[offset]=" + str(lastitem))
        if "err" in data:
            xbmcgui.Dialog().notification("ČRo","Problém při načtení programu", xbmcgui.NOTIFICATION_ERROR, 4000)
            sys.exit()
        if "data" in data and len(data["data"]) > 0:
            lastitem = data["meta"]["count"]
            for item in data["data"]:
                maxdate = parse_date(item["attributes"]["since"]).strftime("%d.%m.%Y")
        return parse_datetime(mindate), parse_datetime(maxdate)
    else:
        xbmcgui.Dialog().notification("ČRo","Problém při načtení programu", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()

