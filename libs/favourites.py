# -*- coding: utf-8 -*-
import os                     
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc

import codecs
import json

from libs.shows import get_show
from libs.utils import get_url
_url = sys.argv[0]
_handle = int(sys.argv[1])

addon = xbmcaddon.Addon(id='plugin.audio.cro')
addon_userdata_dir = xbmc.translatePath(addon.getAddonInfo('profile'))

def list_favourites(label):
    xbmcplugin.setPluginCategory(_handle, label)        
    favourites = get_favourites()
    favourites_ordered = {}
    for key in favourites:
        favourites_ordered.update({ key : favourites[key]["title"] })

    for showId in sorted(favourites_ordered, key=favourites_ordered.get):
        show = favourites[showId]

        list_item = xbmcgui.ListItem(label=show["title"])
        list_item.setArt({ "thumb" : show["img"], "icon" : show["img"] })
        list_item.setInfo( "video", { "title" : show["title"], "director" : [show["director"]], "plot" : show["description"], "studio" : show["station"] })
        if len(show["cast"]) > 0:
            list_item.setInfo( "video", { "cast" : show["cast"] })   
        menus = [("Odstranit z oblíbených", "RunPlugin(plugin://plugin.audio.cro?action=delete_favourites&showId=" + str(show["id"]) + ")")]
        list_item.addContextMenuItems(menus)
        url = get_url(action='list_show', showId = show["id"], page = 1, label = show["title"].encode("utf-8"))                
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

