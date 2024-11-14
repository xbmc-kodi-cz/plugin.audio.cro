# -*- coding: utf-8 -*-
import os                     
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
  
try:
    from urlparse import parse_qsl
except ImportError:
    from urllib.parse import parse_qsl

from libs.utils import get_url
from libs.live import list_live
from libs.program import list_program, list_program_week, list_program_day, program_set_week
from libs.topics import list_topics, list_topic, list_topic_recommended
from libs.shows import list_show, list_shows_menu, list_shows_stations, list_shows_stations_shows
from libs.search import list_search, list_search_title, list_search_person, do_search, do_search_person, delete_search, delete_search_person
from libs.favourites import list_favourites, add_favourites, delete_favourites, list_favourites_new, set_listened_all, set_others, get_favourites
from libs.stations import list_stations, toogle_station
from libs.player import play, play_live

_url = sys.argv[0]
_handle = int(sys.argv[1])
addon = xbmcaddon.Addon(id='plugin.audio.cro')

def list_menu():
    icons_dir = os.path.join(addon.getAddonInfo('path'), 'resources','images')

    list_item = xbmcgui.ListItem(label="Živě")
    url = get_url(action='list_live', label = "Živě")  
    list_item.setArt({ "thumb" : os.path.join(icons_dir , 'live.png'), "icon" : os.path.join(icons_dir , 'live.png') })    
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    # list_item = xbmcgui.ListItem(label="Program")
    # url = get_url(action='list_program', label = "Program")  
    # xbmcplugin.addDirectoryItem(_handle, url, list_item, True)    

    list_item = xbmcgui.ListItem(label="Pořady")
    url = get_url(action='list_shows_stations', label = "Pořady")  
    list_item.setArt({ "thumb" : os.path.join(icons_dir , 'shows.png'), "icon" : os.path.join(icons_dir , 'shows.png') })
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    list_item = xbmcgui.ListItem(label="Témata")
    url = get_url(action='list_topics', label = "Témata")  
    list_item.setArt({ "thumb" : os.path.join(icons_dir , 'themes.png'), "icon" : os.path.join(icons_dir , 'themes.png') })
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    list_item = xbmcgui.ListItem(label="Vyhledávání")
    url = get_url(action='list_search_title', label = "Vyhledávání")  
    list_item.setArt({ "thumb" : os.path.join(icons_dir , 'search.png'), "icon" : os.path.join(icons_dir , 'search.png') })
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    list_item = xbmcgui.ListItem(label="Oblíbené pořady")
    url = get_url(action='list_favourites', label = "Oblíbené")  
    list_item.setArt({ "thumb" : os.path.join(icons_dir , 'favourites.png'), "icon" : os.path.join(icons_dir , 'favourites.png') })  
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)   

    others_favourites = get_favourites(others = 1)
    if len(others_favourites) > 0:
        list_item = xbmcgui.ListItem(label="Ostatní oblíbené pořady")
        url = get_url(action='list_favourites', label = "Ostatní", others = 1)
        list_item.setArt({ "thumb" : os.path.join(icons_dir , 'favourites_others.png'), "icon" : os.path.join(icons_dir , 'favourites_others.png') })  
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)         

    if addon.getSetting("hide_favourites_new") == "false":
        list_item = xbmcgui.ListItem(label="Nejnovější epizody oblíbených pořadů")
        url = get_url(action='list_favourites_new', label = "Nejnovější")  
        list_item.setArt({ "thumb" : os.path.join(icons_dir , 'favourites_new.png'), "icon" : os.path.join(icons_dir , 'favourites_new.png') })  
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)       


    if addon.getSetting("hide_stations_settings") == "false":
        list_item = xbmcgui.ListItem(label="Nastavení stanic")
        url = get_url(action='list_stations', label = "Nastavení stanic")  
        list_item.setArt({ "thumb" : os.path.join(icons_dir , 'settings.png'), "icon" : os.path.join(icons_dir , 'settings.png') })
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
            if "mark_new" in params:
                list_show(params["showId"], params["page"], params["label"], params["mark_new"])   
            else:
                list_show(params["showId"], params["page"], params["label"])   

        elif params['action'] == 'list_search':
            list_search(params["label"])
        elif params['action'] == 'list_search_title':
            list_search_title(params["label"])    
        elif params['action'] == 'list_search_person':
            list_search_person(params["label"])                       
        elif params['action'] == 'do_search':
            do_search(params["query"], params["label"])
        elif params['action'] == 'do_search_person':
            do_search_person(params["query"], params["label"])            
        elif params['action'] == 'delete_search':
            delete_search(params["query"])
        elif params['action'] == 'delete_search_person':
            delete_search_person(params["query"])            

        elif params['action'] == 'list_favourites':
            if "others" in params:
                list_favourites(params["label"], params["others"])        
            else:
                list_favourites(params["label"])        
        elif params['action'] == 'add_favourites':
            add_favourites(params["showId"], params["others"])                    
        elif params['action'] == 'delete_favourites':
            delete_favourites(params["showId"])     
        elif params['action'] == 'list_favourites_new':
            list_favourites_new(params["label"])                  
        elif params['action'] == 'set_listened_all':
            set_listened_all(params["showId"])
        elif params['action'] == 'set_others':
            set_others(params["showId"], params["val"])            

        elif params['action'] == 'list_stations':
            list_stations(params["label"])
        elif params['action'] == 'toogle_station':
            toogle_station(params["stationId"])

        elif params['action'] == 'play':
            play(params["url"], params["showId"], params["episodeId"], params["title"], params["img"])
        elif params['action'] == 'play_live':
            play_live(params["url"], params["title"], params["img"])

        else:
            raise ValueError('Neznámý parametr: {0}!'.format(paramstring))
    else:
        list_menu()

if __name__ == '__main__':
    router(sys.argv[2][1:])
