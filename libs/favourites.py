# -*- coding: utf-8 -*-
import os                     
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc

import codecs
import json
from datetime import datetime
import time
import sqlite3

from libs.shows import get_show
from libs.utils import get_url, call_api, parse_date
_url = sys.argv[0]
_handle = int(sys.argv[1])

addon = xbmcaddon.Addon(id='plugin.audio.cro')
addon_userdata_dir = xbmc.translatePath(addon.getAddonInfo('profile'))

current_version = 1
def open_db():
    global db, version
    db = sqlite3.connect(addon_userdata_dir + "listened.db", timeout = 20)
    db.execute('CREATE TABLE IF NOT EXISTS version (version INTEGER PRIMARY KEY)')
    db.execute('CREATE TABLE IF NOT EXISTS listened (episodeId VARCHAR PRIMARY KEY, showId VARCHAR)')
    row = None
    for row in db.execute('SELECT version FROM version'):
      version = row[0]
    if not row:
        db.execute('INSERT INTO version VALUES (?)', [current_version])
        db.commit()     
        version = current_version
    if version != current_version:
      version = migrate_db(version)
    db.commit()     

def close_db():
    global db
    db.close()    

def migrate_db(version):
    global db
    # if version == 0:
    #   version = 1
    #   db.execute('UPDATE version SET version = ?', str(version))
    #   db.commit()   
    # if version == 1:
    #   version = 2
    #   try:
    #     db.execute('ALTER TABLE queue ADD COLUMN pvrProgramId INTEGER')
    #   except OperationalError:
    #     pass
    #   db.execute('UPDATE version SET version = ?', str(version))
    #   db.commit()           
    return version

def list_favourites(label):
    xbmcplugin.setPluginCategory(_handle, label)        
    favourites = get_favourites()
    favourites_ordered = {}
    for key in favourites:
        favourites_ordered.update({ key : favourites[key]["title"] })
    for showId in sorted(favourites_ordered, key=favourites_ordered.get):
        show = favourites[showId]
        
        if addon.getSetting("hide_unlistened_favourites") == "false":
            unlistened = get_unlistened_count(showId)
            if unlistened > 0 :
                list_item = xbmcgui.ListItem(label=show["title"] + " (" + str(unlistened) + " nových)")
            else:
                list_item = xbmcgui.ListItem(label=show["title"])            
        else:
            list_item = xbmcgui.ListItem(label=show["title"])            
        list_item.setArt({ "thumb" : show["img"], "icon" : show["img"] })
        list_item.setInfo( "video", { "title" : show["title"], "director" : [show["director"]], "plot" : show["description"], "studio" : show["station"] })
        if len(show["cast"]) > 0:
            list_item.setInfo( "video", { "cast" : show["cast"] })   
        menus = [("Odstranit z oblíbených", "RunPlugin(plugin://plugin.audio.cro?action=delete_favourites&showId=" + str(show["id"]) + ")")]
        if addon.getSetting("hide_unlistened_favourites") == "false":
            menus.append(("Označit epizody jako poslechnuté", "RunPlugin(plugin://plugin.audio.cro?action=set_listened_all&showId=" + str(show["id"]) + ")"))
        list_item.addContextMenuItems(menus)
        if addon.getSetting("hide_unlistened_favourites") == "false":
            url = get_url(action='list_show', showId = show["id"], page = 1, label = show["title"].encode("utf-8"), mark_new = 1)   
        else:
            url = get_url(action='list_show', showId = show["id"], page = 1, label = show["title"].encode("utf-8"), mark_new = 0)                            
        list_item.setContentLookup(False) 
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)      
    xbmcplugin.endOfDirectory(_handle) 

def delete_favourites(showId):
    filename = addon_userdata_dir + "favourites.txt"
    favourites = get_favourites()
    err = 0
    if showId in favourites.keys():
        del favourites[showId]
        try:
            with codecs.open(filename, "w", encoding="utf-8") as file:
                data = json.dumps(favourites)
                file.write('%s\n' % data)
        except IOError:
            err = 1
            xbmcgui.Dialog().notification("ČRo","Problém při uložení oblíbených pořadů", xbmcgui.NOTIFICATION_ERROR, 4000)
        if err == 0:
            xbmcgui.Dialog().notification("ČRo","Pořad byl odebrán z oblíbených", xbmcgui.NOTIFICATION_INFO, 4000)            
        xbmc.executebuiltin('Container.Refresh')
    xbmcgui.Dialog().notification("ČRo","Odstraňovaný pořad nebyl nalezen", xbmcgui.NOTIFICATION_ERROR, 4000)


def add_favourites(showId):
    filename = addon_userdata_dir + "favourites.txt"
    favourites = get_favourites()
    err = 0
    if showId not in favourites.keys():
        show = get_show(showId)
        favourites.update({ showId : show })
        try:
            with codecs.open(filename, "w", encoding="utf-8") as file:
                data = json.dumps(favourites)
                file.write('%s\n' % data)
        except IOError:
            err = 1
            xbmcgui.Dialog().notification("ČRo","Problém při uložení oblíbených pořadů", xbmcgui.NOTIFICATION_ERROR, 4000)
        if err == 0:
            xbmcgui.Dialog().notification("ČRo","Pořad byl přidán do oblíbených", xbmcgui.NOTIFICATION_INFO, 4000)            

def get_favourites():
    filename = addon_userdata_dir + "favourites.txt"
    try:
        with open(filename, "r") as file:
            for line in file:
                item = line[:-1]
                data = json.loads(item)
    except IOError:
        data = {}
    return data    

def list_favourites_new(label):
    items = int(addon.getSetting("favourites_new_count"))
    xbmcplugin.setPluginCategory(_handle, label)        
    favourites = get_favourites()
    episodes = {}
    episodes_ordered = {}
    for showId in favourites:
        show = favourites[showId]
        data = call_api(url = "https://api.mujrozhlas.cz/shows/" + showId + "/episodes?sort=-since&page[limit]=" + str(items))
        if "err" in data:
            xbmcgui.Dialog().notification("ČRo","Problém při získání pořadů", xbmcgui.NOTIFICATION_ERROR, 4000)
            sys.exit()
        if "data" in data and len(data["data"]) > 0:      
            for episode in data["data"]:
                if "attributes" in episode and "title" in episode["attributes"] and len(episode["attributes"]["title"]) > 0:
                    starttime =  parse_date(episode["attributes"]["since"])
                    starttime_ts = time.mktime(starttime.timetuple())
                    episodes_ordered.update({ episode["id"] : starttime_ts})
                    if "mirroredSerial" in episode["attributes"] and "totalParts" in episode["attributes"]["mirroredSerial"] and "part" in episode["attributes"]:
                        parts =  " (" + str(episode["attributes"]["part"]) + "/" + str(episode["attributes"]["mirroredSerial"]["totalParts"]) + ") "
                    else:
                        parts = ""    
                    title = episode["attributes"]["title"] + parts + " (" + starttime.strftime("%d.%m.%Y %H:%M") + ")"
                    link = episode["attributes"]["audioLinks"][0]["url"]
                    episodes.update({ episode["id"] : { "showId" : showId, "link" : link, "img" : show["img"], "tvshowtitle" : show["title"], "title" : title, "aired" : starttime.strftime("%Y-%m-%d"), "director" : [show["director"]] , "plot" : show["description"], "studio" : show["station"] }})

    if len(episodes) > 0:
        for key in sorted(episodes_ordered, key=episodes_ordered.get, reverse=True):  
            list_item = xbmcgui.ListItem(label=episodes[key]["title"])
            list_item.setArt({ "thumb" : episodes[key]["img"], "icon" : episodes[key]["img"] })
            list_item.setInfo( "video", { "tvshowtitle" : episodes[key]["tvshowtitle"], "title" : episodes[key]["title"], "aired" : episodes[key]["aired"], "director" : episodes[key]["director"] , "plot" : episodes[key]["plot"], "studio" : episodes[key]["studio"] })
            list_item.setProperty("IsPlayable", "true")
            list_item.setContentLookup(False)
            url = get_url(action='play', url = episodes[key]["link"].encode("utf-8"), showId = episodes[key]["showId"], episodeId = key) 
            xbmcplugin.addDirectoryItem(_handle, url, list_item, False)
    xbmcplugin.endOfDirectory(_handle)

def set_listened(episodeId, showId):
    open_db()
    row = None
    found = 0
    for row in db.execute('SELECT episodeId FROM listened WHERE episodeId = ?', [str(episodeId)]):
      found = 1
    if row == None or found == 0:
        db.execute('INSERT INTO listened VALUES (?, ?)', [episodeId, showId])
        db.commit()
    close_db() 

def get_listened(episodeId):
    open_db()
    row = None
    found = 0
    for row in db.execute('SELECT episodeId FROM listened WHERE episodeId = ?', [str(episodeId)]):
      found = 1
    close_db()
    if found == 0:
        return False
    else: 
        return True


def get_unlistened_count(showId):
    items_count = 0
    new = 0
    data = call_api(url = "https://api.mujrozhlas.cz/shows/" + showId + "/episodes?sort=-since&page[limit]=1&page[offset]=0")
    if "err" in data:
        xbmcgui.Dialog().notification("ČRo","Problém při získání pořadů", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()
    if "data" in data and len(data["data"]) > 0:      
        items_count = int(data["meta"]["count"])

    open_db()
    listened_count = 0
    row = None
    for  row in db.execute('SELECT count(1) pocet FROM listened WHERE showId = ?', [str(showId)]):
      listened_count = int(row[0])
    close_db()

    new = items_count - listened_count
    return new

def set_listened_all(showId):
    items_count = 0
    offset = 0
    episodeIds = []
    data = call_api(url = "https://api.mujrozhlas.cz/shows/" + showId + "/episodes?sort=-since&page[limit]=1&page[offset]=0")
    if "err" in data:
        xbmcgui.Dialog().notification("ČRo","Problém při získání pořadů", xbmcgui.NOTIFICATION_ERROR, 4000)
        sys.exit()
    if "data" in data and len(data["data"]) > 0:      
        items_count = int(data["meta"]["count"])

    if items_count > 0:
        while offset < items_count:
            data = call_api(url = "https://api.mujrozhlas.cz/shows/" + showId + "/episodes?sort=-since&page[limit]=100&page[offset]=" + str(offset))
            if "err" in data:
                xbmcgui.Dialog().notification("ČRo","Problém při získání pořadů", xbmcgui.NOTIFICATION_ERROR, 4000)
                sys.exit()
            if "data" in data and len(data["data"]) > 0:
                for episode in data["data"]:
                    episodeIds.append(episode["id"])  
            offset = offset + 100  

        for episodeId in episodeIds:
            if not get_listened(episodeId):  
                set_listened(episodeId, showId)
    xbmc.executebuiltin('Container.Refresh')


