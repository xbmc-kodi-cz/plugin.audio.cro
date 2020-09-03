# -*- coding: utf-8 -*-
import os                     
import sys
import xbmc
import xbmcaddon

import json
from urllib import urlencode, quote
from urllib2 import urlopen, Request, HTTPError

from datetime import datetime, timedelta


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

def call_api(url):
    header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0", "Content-Type":"application/json"}
    request = Request(url = url , data = None, headers = header)
    if addon.getSetting("log_request") == "true":
      xbmc.log(url)
    try:
      html = urlopen(request).read()
      if addon.getSetting("log_response") == "true":
        xbmc.log(html)      
      if html and len(html) > 0:
        data = json.loads(html)
        return data
      else:
        return []
    except HTTPError as e:
      return { "err" : e.reason }  

def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urlencode(kwargs))