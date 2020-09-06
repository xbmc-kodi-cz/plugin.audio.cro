# -*- coding: utf-8 -*-
import os                     
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmc

from urlparse import parse_qsl

from libs.utils import get_url, call_api
from libs.live import list_live
from libs.program import list_program, list_program_week, list_program_day, program_set_week
from libs.topics import list_topics, list_topic, list_topic_recommended
from libs.shows import list_show, list_shows_menu, list_shows_stations, list_shows_stations_shows
from libs.search import list_search, do_search
from libs.stations import list_stations, toogle_station
from libs.player import play

_url = sys.argv[0]
_handle = int(sys.argv[1])
addon = xbmcaddon.Addon(id='plugin.audio.cro')

def list_menu():
    list_item = xbmcgui.ListItem(label="Živě")
    url = get_url(action='list_live', label = "Živě")  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    # list_item = xbmcgui.ListItem(label="Program")
    # url = get_url(action='list_program', label = "Program")  
    # xbmcplugin.addDirectoryItem(_handle, url, list_item, True)    

    list_item = xbmcgui.ListItem(label="Pořady")
    url = get_url(action='list_shows_stations', label = "Pořady")  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    list_item = xbmcgui.ListItem(label="Témata")
    url = get_url(action='list_topics', label = "Témata")  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    list_item = xbmcgui.ListItem(label="Vyhledávání")
    url = get_url(action='list_search', label = "Vyhledávání")  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    if addon.getSetting("hide_stations_settings") == "false":
        list_item = xbmcgui.ListItem(label="Nastavení stanic")
        url = get_url(action='list_stations', label = "Nastavení stanic")  
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)    

    xbmcplugin.endOfDirectory(_handle)

def router(paramstring):
    params = dict(parse_qsl(paramstring))
    if params:
        if params['action'] == 'list_live':
            list_live(params["label"]) 

        elif params['action'] == 'list_program':
            list_program(params["label"]) 
        elif params['action'] == 'list_program_week':
            list_program_week(params["stationId"], params["startdate"], params["enddate"], params["label"])                 
        elif params['action'] == 'list_program_day':
            list_program_day(params["stationId"], params["day"], params["label"])    
        elif params['action'] == 'program_set_week':
            program_set_week(params["stationId"], params["startdate"], params["enddate"], params["label"])    


        elif params['action'] == 'list_topics':
            list_topics(params["label"]) 
        elif params['action'] == 'list_topic':
            list_topic(params["topicId"], params["label"])             
        elif params['action'] == 'list_topic_recommended':
            list_topic_recommended(params["topicId"], params["filtr"], params["label"])             

        elif params['action'] == 'list_shows_menu':
            list_shows_menu(params["label"])  
        elif params['action'] == 'list_shows_stations':
            list_shows_stations(params["label"])  
        elif params['action'] == 'list_shows_stations_shows':
            list_shows_stations_shows(params["stationId"], params["page"], params["label"])  

        elif params['action'] == 'list_show':
            list_show(params["showId"], params["label"])   

        elif params['action'] == 'list_search':
            list_search(params["label"])
        elif params['action'] == 'do_search':
            do_search(params["query"], params["label"])

        elif params['action'] == 'list_stations':
            list_stations(params["label"])
        elif params['action'] == 'toogle_station':
            toogle_station(params["stationId"])

        elif params['action'] == 'play':
            play(params["url"])

        else:
            raise ValueError('Neznámý parametr: {0}!'.format(paramstring))
    else:
        list_menu()

if __name__ == '__main__':
    router(sys.argv[2][1:])
