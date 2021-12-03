# -*- coding: utf-8 -*-
import os                     
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc

from datetime import datetime

from libs.utils import get_url, call_api, parse_date, encode
from libs.stations import get_stations

_url = sys.argv[0]
_handle = int(sys.argv[1])
addon = xbmcaddon.Addon(id='plugin.audio.cro')

def list_live(label):
    xbmcplugin.setPluginCategory(_handle, label)   
    stations, stations_nums  = get_stations(filtered=1)
    schedule = get_current_schedule()
    urls = get_urls()
    for num in sorted(stations_nums.keys()):
        info = {}
        if stations[stations_nums[num]]["id"] in urls:
            if stations[stations_nums[num]]["id"] in schedule:
                title = stations[stations_nums[num]]["title"] + " - " + schedule[stations[stations_nums[num]]["id"]]["show"] + " (" + schedule[stations[stations_nums[num]]["id"]]["start"] + " - " + schedule[stations[stations_nums[num]]["id"]]["end"] + ")"
                info = { "title" : schedule[stations[stations_nums[num]]["id"]]["show"], "plot" : schedule[stations[stations_nums[num]]["id"]]["title"] }
            else:
                title = stations[stations_nums[num]]["title"]
            list_item = xbmcgui.ListItem(label=title)
            if "img" in stations[stations_nums[num]] and len(stations[stations_nums[num]]["img"]) > 0:
                img = stations[stations_nums[num]]["img"]
                list_item.setArt({ "thumb" : img, "icon" : img })
            else:
                img = "xxx"       
            url = get_url(action='play_live', url = urls[stations[stations_nums[num]]["id"]], title = encode(title), img = img)  

            if len(info) > 0:
                list_item.setInfo("music", info)
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    xbmcplugin.endOfDirectory(_handle)        

def get_current_schedule():
    schedule = {}
    data = call_api(url = "https://api.mujrozhlas.cz/schedule-current")
    if "err" in data:
        xbmcgui.Dialog().notification("ČRo","Problém při načtení programu", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()
    if "data" in data and len(data["data"]) > 0:
        for item in data["data"]:
            now = datetime.now()
            if now > parse_date(item["attributes"]["since"]) and now < parse_date(item["attributes"]["till"]):
                if "show" in item["relationships"]:
                    showId = item["relationships"]["show"]["data"]["id"]
                else:
                    showId = "N/A"

                schedule.update({ item["relationships"]["station"]["data"]["id"] : { "showId" : showId, "show" : item["attributes"]["mirroredShow"]["title"], "title" : item["attributes"]["title"], "start" : parse_date(item["attributes"]["since"]).strftime("%H:%M"), "end" : parse_date(item["attributes"]["till"]).strftime("%H:%M") }})
    else:
        xbmcgui.Dialog().notification("ČRo","Problém při načtení programu", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()
    return schedule    

def get_urls():
    urls = {}
    data = call_api(url = "https://api.mujrozhlas.cz/stations")
    if "err" in data:
        xbmcgui.Dialog().notification("ČRo","Problém při načtení streamu", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()
    if "data" in data and len(data["data"]):
        for station in data["data"]:
            if "attributes" in station and "audioLinks" in station["attributes"] and len(station["attributes"]["audioLinks"]) > 0:
                url = ""
                aac_urls = {}
                mp3_urls = {}
                for audiolink in station["attributes"]["audioLinks"]:
                    if audiolink["linkType"] == "directstream" and len(url) == 0:
                        if audiolink["variant"] == 'aac':
                            aac_urls.update({ audiolink["bitrate"] : audiolink["url"] })
                        if audiolink["variant"] == 'mp3':
                            mp3_urls.update({ audiolink["bitrate"] : audiolink["url"] })
                    if audiolink["variant"] == "mp3"  and  audiolink["linkType"] == "directstream" and len(url) == 0:
                        url = audiolink["url"] 
                if addon.getSetting("prefer_aac") == "true":
                    if len(aac_urls) > 0:
                        url = aac_urls[max(aac_urls.keys())]
                    elif len(mp3_urls):
                        url = mp3_urls[max(mp3_urls.keys())]
                else:
                    if len(mp3_urls) > 0:
                        url = mp3_urls[max(mp3_urls.keys())]
                    elif len(aac_urls):
                        url = aac_urls[max(aac_urls.keys())]
                if len(url) > 1:
                    urls.update({ station["id"] : url})
    return urls