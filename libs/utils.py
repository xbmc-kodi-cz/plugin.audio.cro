# -*- coding: utf-8 -*-
import os                     
import sys
import xbmcgui
import xbmc
import xbmcaddon

import json

try:
    from xbmcvfs import translatePath
except ImportError:
    from xbmc import translatePath
  
try:
    from urllib2 import urlopen, Request, HTTPError
    from urllib import urlencode, quote
except ImportError:
    from urllib.request import urlopen, Request
    from urllib.parse import urlencode, quote
    from urllib.error import HTTPError

from datetime import datetime, timedelta

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

_url = sys.argv[0]
addon = xbmcaddon.Addon(id='plugin.audio.cro')

def parse_date(date):
    year = int(date[0:4])
    month = int(date[5:7])
    day = int(date[8:10])
    hour = int(date[11:13])
    minute = int(date[14:16])
    second = int(date[17:19])
    return datetime(year, month, day, hour, minute, second)

def parse_datetime(date):
    day = int(date[0:2])
    month = int(date[3:5])
    year = int(date[6:10])
    return datetime(year, month, day)    

def call_api(url):
    header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0", "Content-Type":"application/json"}
    request = Request(url = url , data = None, headers = header)
    if addon.getSetting("log_request") == "true":
        xbmc.log(url)
    try:
        html = urlopen(request).read()
        if addon.getSetting("log_response") == "true":
            xbmc.log(str(html))      
        if html and len(html) > 0:
            data = json.loads(html)
            return data
        else:
            return []
    except HTTPError as e:
        return { "err" : e.reason }  

def get_userdata_dir():
    addon_userdata_dir = translatePath(addon.getAddonInfo('profile'))
    if os.path.exists(addon_userdata_dir) == False: 
        try:
            os.mkdir(addon_userdata_dir)
        except OSError:
            xbmcgui.Dialog().notification("ČRo","Problém při vytvoření nastavení", xbmcgui.NOTIFICATION_ERROR, 3000)
    return addon_userdata_dir

def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urlencode(kwargs))

def decode(string_to_decode):
    if PY2:
        return string_to_decode.decode("utf-8")
    else:
        return string_to_decode

def encode(string_to_encode):
    if PY2:
        return string_to_encode.encode("utf-8")
    else:
        return string_to_encode  
