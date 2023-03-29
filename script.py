#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import argparse


# from requests import Session
import requests
import re
import os
import subprocess
import json
import time
import datetime
# import dataclasses
from pprint import pprint
from functools import partial
from pathlib import Path
from operator import itemgetter
from collections import defaultdict
# from typing import List
# from itertools import chain
try:
    import jsbeautifier

except:
    jsbeautifier = None
    
import dataclasses

# import collections.abc
# import contextlib
# import itertools.chain
# from yt_dlp.utils import traverse_obj


    

tz_tokyo = datetime.timezone(datetime.timedelta(hours=9))

headers={"authorization": "bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkZXYiOiI5ZWRjMzAzOC1jN2M5LTRiZTgtYjM3ZS00YzExMjA1ZDE4ODYiLCJleHAiOjIxNDc0ODM2NDcsImlzcyI6ImFiZW1hLmlvL3YxIiwic3ViIjoiOW9YZ0RMTnpwR1lnR3cifQ.mmasFiTeb5QpcmJgmNRup_o5MMCiEmlIZT-nqKuusXc"}

# abema_tt_fold = Path("abema", "timetable",)

now = datetime.datetime.now(tz=tz_tokyo)

fromtimestamp = partial(datetime.datetime.fromtimestamp, tz=tz_tokyo)


class Fold:
    abema_tt = Path("abema", "timetable",)
    

def js_open(js):
    if isinstance(js, (str, Path)):
        with open(js,'rt') as f:#, errors='ignore',encoding='unicode-escape'
            D1 = json.load(f)#object_pairs_hook=OrderedDict 
    return D1

def js_write(dic, js):
    if isinstance(js, (str, Path)):
        js = Path(js)
        js.parent.mkdir(exist_ok=True, parents=True)
        with open(js, 'w') as f:
            json.dump(dic, f,indent=4, ensure_ascii=False)


class AbemaTable:
    def __init__(self, table_json):
        self.table = table_json
        # self.channels = self.table["channels"]
        for k, v in self.table.items():
            setattr(self, k, v)
    
        
            
    @classmethod
    def set(cls):
        res = requests.get("https://api.p-c3-e.abema-tv.com/v1/timetable/dataSet?debug=false",headers=headers)
        table_json = res.json()
        return cls(table_json)
        
# 175-1rthzhecdme

def get_abema_timetable():
    res = requests.get("https://api.p-c3-e.abema-tv.com/v1/timetable/dataSet?debug=false",headers=headers)
    program = res.json()
    pub_at = datetime.datetime.fromtimestamp(program['publishedAt'], tz=tz_tokyo)
    
    timetable_path = Path("abema", "timetable","whole", pub_at.strftime("%y%m%d%H")+".json")
    timetable_path.parent.mkdir(exist_ok=True, parents=True)
    js_write(program, timetable_path)
    t = AbemaTable(program)
    
    stock = defaultdict(lambda:defaultdict(list))
    for slot in t.slots:
        date_fmt = "%Y%m%d"
        start = fromtimestamp(slot['startAt']).strftime(date_fmt)
        end = fromtimestamp(slot['endAt']).strftime(date_fmt)
        if start in t.availableDates :
            stock[start][slot['channelId']].append(slot)
        if end != start and end in t.availableDates:
            stock[end][slot['channelId']].append(slot)    
    for k,v in stock.items():
        j = {"pubAt": t.publishedAt, "pubDate": fromtimestamp(t.publishedAt).strftime("%Y%m%d%H"),"slots":[]}
        j["slots"] = v
        timetable_path = Fold.abema_tt/ "part"/ k+".json"
        timetable_path.parent.mkdir(exist_ok=True, parents=True)
        if timetable_path.exists():
            j2 = js_open(timetable_path)
            if j["slots"] != j2["slots"]:
                js_write(j, timetable_path)

    
def get_abema_timetable02():
    res = requests.get("https://api.p-c3-e.abema-tv.com/v1/timetable/dataSet?debug=false",headers=headers)
    program = res.json()
    # program["slotsGroup"].sort(key=itemgetter("id")
    
    pub_at = fromtimestamp(program['publishedAt'])
    
    timetable_path = Path("abema", "timetable","whole", pub_at.strftime("%y%m%d%H")+".json")
    timetable_path.parent.mkdir(exist_ok=True, parents=True)
    js_write(program, timetable_path)
    return AbemaTable(program)
    
def split_abema_timetable(t:AbemaTable):
    stock = defaultdict(lambda:defaultdict(list))
    for slot in t.slots:
        date_fmt = "%Y%m%d"
        start = fromtimestamp(slot['startAt']).strftime(date_fmt)
        end = fromtimestamp(slot['endAt']).strftime(date_fmt)
        if start in t.availableDates :
            stock[start][slot['channelId']].append(slot)
        if end != start and end in t.availableDates:
            stock[end][slot['channelId']].append(slot)    
    for k,v in stock.items():
        j = {"pubAt": t.publishedAt, "pubDate": fromtimestamp(t.publishedAt).strftime("%Y%m%d%H")}
        j["slots"] = v
        timetable_path = Fold.abema_tt/ "part"/ f"{k}.json"
        timetable_path.parent.mkdir(exist_ok=True, parents=True)
        if timetable_path.exists():
            j2 = js_open(timetable_path)
            if j["slots"] != j2["slots"]:
                js_write(j, timetable_path)
        else:
            js_write(j, timetable_path)
            
def split_abema_timetable02(t:AbemaTable):
    # stock = defaultdict(lambda:defaultdict(list))
    stock = {d :{c['id']:[] for c in t.channels if "anime" in c['id']}
             for d in t.availableDates}
    date_fmt = "%Y%m%d"
    for slot in t.slots:
        del slot['displayImageUpdatedAt']
        
        start = fromtimestamp(slot['startAt']).strftime(date_fmt)
        end = fromtimestamp(slot['endAt']).strftime(date_fmt)
        try: 
            if start in t.availableDates :
                stock[start][slot['channelId']].append(slot)
            if end != start and end in t.availableDates:
                stock[end][slot['channelId']].append(slot)   
        except:
            continue
    for k,v in stock.items():
        j = {"pubAt": t.publishedAt, "pubDate": fromtimestamp(t.publishedAt).strftime("%Y%m%d%H")}
        j["slots"] = v
        [c['id'] for c in t.channels]
        timetable_path = Fold.abema_tt/ "part"/ f"{k}.json"
        timetable_path.parent.mkdir(exist_ok=True, parents=True)
        if timetable_path.exists():
            j2 = js_open(timetable_path)
            if j["slots"] != j2["slots"]:
                js_write(j, timetable_path)
        else:
            js_write(j, timetable_path)
            
def allanime():
##    if free:
##        url = 'https://api.abema.io/v1/video/featureGenres/animation/cards?\
##onlyFree=false&limit=20&next='
##    else:
##        url = 'https://api.abema.io/v1/video/featureGenres/animation/cards?\
##onlyFree=true&limit=20&next=
    
    nextq = ''
    js, nextq = nextver(nextq,limit=40)
    jss = []
    jss.append(js)
    while True:
        try:
            js, nextq = nextver(nextq)
            jss.append(js)
        except:
            break
    return jss

def allanime02():
    
    def append01(jss, js):
        jss["items"].extend(js["cards"])
        
    def append02(jss, js):
        need_keys = ['seriesId', 'title', 'label', 'onDemandTypes']
        for item in js["cards"]:
            # out_item = {}
            # for k in item.keys():
                # if k in need_keys:
                    # out_item[k] = item[k]
                    
            out_item = {k:item[k] for k in item.keys() if k in need_keys}
            
            jss["items"].append(out_item)
            
            
        
    nextq = ''
    js, nextq = nextver(nextq,limit=40)
    jss = {}
    jss["genre"] = js["genre"]
    jss["pubAt"] =  now.strftime("%Y%m%d%H")
    jss["items"] = []
    append02(jss, js)
    while True:
        try:
            js, nextq = nextver(nextq)
            append02(jss, js)
        except:
            break
    jss["items"].sort(key=itemgetter('seriesId'))
    return jss
    


def nextver(nextq="", limit=20):
        url = 'https://api.abema.io/v1/video/featureGenres/animation/cards?\
    onlyFree=false&limit={}&next={}'.format(limit,nextq)
        js = requests.get(url, headers=headers).json()
        
        # F(js)
        result = js['paging']['next']
        return js, result            
        
def save_abema_allanime(out=False):

        
    def urltojs(url):
        res = requests.get(url, headers=headers)
        js = res.json(**{"object_pairs_hook" : OrderedDict})
        
        return js
    
    jss = allanime02()
    # jss["items"].sort(key=itemgetter('seriesId'))
    filepath = Path("abema", "all-anime", "{}.json".format(jss["pubAt"]))
    filepath.parent.mkdir(exist_ok=True, parents=True)
    js_write(jss, filepath)
    
    
    filepath = Path("abema", "all-anime.json")
    save_renew(jss, filepath)
    # program = jss
    # if file_path.exists():
        # program2 = js_open(file_path)
        # if program["items"] != program2["items"]:
            # js_write(program, file_path)
    # else:
        # js_write(program, file_path)

    if out:
        return jss
        
def save_renew(program, filepath: Path, attr="items"):
    filepath.parent.mkdir(exist_ok=True, parents=True)
    
    if filepath.exists():
        program2 = js_open(filepath)
        if json_data[attr] != program2[attr]:
            js_write(program, filepath)
            return True
        return False
    else:
        js_write(program, filepath)
        return True
        

def search(t, key, ranges=100, start=0):
    i = t.index(key,start)
    # print(i)
    print(t[i-ranges:i])
    print("-"*10)
    print(t[i:i+ranges])
    return i
    

    
# https://anime.nicovideo.jp/period/other.html

       
# get_abema_timetable()
    
    

from bs4 import BeautifulSoup

class Niconico:
    baseurl = 'https://anime.nicovideo.jp'
    
class NicoList:
    period_url = 'https://anime.nicovideo.jp/period/{}-{}.html'
    seasons = ["winter", "spring", "summer", "autumn"]
    s = [2018, 1]
    other = "https://anime.nicovideo.jp/period/other.html"

    @staticmethod
    def _extract_info_base(item):
        return _extract_info_base(item)
        
    @staticmethod
    def _extract_info(base):
        return _extract_info(base)
        
    @staticmethod    
    def next_season(year, season):
        if self.s >= [year, season]:
            assert(False)
        if season == 3:
            return year+1, 0
        else:
            return year, season+1
    
    @property
    def season(self):
        return self.seasons[self.season_num]
    
    def __init__(self, year=2023, season=0):
        url = "https://anime.nicovideo.jp/period/2023-winter.html"
        self.season_num = season #"winter"
        self.year = year #"2023"
        url = self.period_url.format(year, self.season)
        # url = period_url.format(2023, seasons[0])
        
        res = requests.get(url)
        try:
            res.raise_for_status()
        except requests.exceptions.HTTPError:
            raise AttributeError
        res.encoding = "utf-8"
        self.page = page = res.text
        t = page
        start = t[:t.index("<h2")].rindex('<li')
        self.tag = tag = t[start:start+t[start:].index('>')+1]
        self.soup = BeautifulSoup(page, "html.parser")
        # '<li class="_1Fpuq">'
        # self.sp1 = t[start:].split("<li")
        # self.sp2 = t[start:].split(tag)
        self.sp3 = self.soup.find_all('li', {'class': "_1Fpuq"})
        
        
        
        self.item_list_base = []
        for item in self.sp3:
            base = self._extract_info_base(item)
            self.item_list_base.append(base)
        
        self.item_list = []
        for base in self.item_list_base:
            content = self._extract_info(base)
            self.item_list.append(content)  
            
    def save(self):
        program = {"items": self.item_list, 
                    "pubAt": now.strftime("%Y%m%d%H")}
        timetable_path = Path("niconico", "seasons-list", "{}_{}.json".format(self.year, self.season_num))
        timetable_path.parent.mkdir(exist_ok=True, parents=True)
        
        if timetable_path.exists():
            program2 = js_open(timetable_path)
            if program["items"] != program2["items"]:
                js_write(program, timetable_path)
        else:
            js_write(program, timetable_path)
        
        
        # js_write(program, timetable_path)    
            

            
            
            
            


def _extract_info_base(item):
    base= {}
    # content["_base"] = base
    base["main"] = item.find("a", {"class": "_2R1vQ"})
    base["continue"] = item.find('p', {'class': '_3tUcg'})
    base["title"] = item.find("h2", {"class": "gDySc"})
    base["free"] = item.find('p', {'class': 'nSekS'})            
    base["img"] = item.find('div', {'class': '_3ke9H'})
    base["onair"] = item.find('div', {'class': 'DbW39'})
    base["video"] = item.find('div', {'class': 'J9hxP'})
    base["content"] = item.find('p', {'class': '_bV14'})
    # base["official-url"] = item.find('a', {'class': "pQx9h"})
    return base

def _extract_info(base):
    
    #Noneじゃなくて　
    
    content = {}
    content["url"] = base["main"].get("href")
    # content["continue"] = False if a['_base']["continue"].get('data-type') else True
    content["new"] = True if base["continue"].get('data-type') == "new" else False
    # {'class': '_3tUcg', 'data-type': 'new'}

    content["title"] = base["title"].get_text()
    try:
        content["free"] = (False if base['free'] is None else 
                              True if base['free'].find_next().get("alt") == '無料あり' else False)
        # content["free"] = True if base['free'].find_next().get("alt") == '無料あり' else False
    except:
        print(base["title"])
        print(base['free'])
        content["free"] = False
    
    content["onair"] = [t.get_text() for t in base["onair"].findChildren()] 
    content["onair-details"] = {}
    for t in base["onair"].findChildren():
        # try:
        if "_3tTg4" in t.get("class", []):
            content["onair-details"]["tv"] = t.get_text()
        # elif "ニコ動" in t.get_text():
        elif t.get_text().startswith("ニコ動"):
            # content["onair-details"]["nico"] = t.get_text()
            content["onair-details"]["nico"] = t.get_text()[4:]
        # elif "ニコ動" in t.get_text():
        elif t.get_text().startswith("ニコ生"):
            # content["onair-details"]["nico"] = t.get_text()
            content["onair-details"]["nico-live"] = t.get_text()[4:]
        else:
            content["onair-details"]["other"] = t.get_text()
        # except:
            # print(base["title"])
            # print(base["onair"])
            # content["onair-details"]["other"] = t.get_text()

    # content["onair-tv"] = any("_3tTg4" in t.get("class") for t in base["onair"].findChildren())
    # content["onair-tv"] = content["onair-details"].get("tv")
    
    content["video"] = [li.get_text() for li in base["video"].find_next().findChildren()] 
    content["video-details"] = {}
    for li in base["video"].find_next().findChildren():
        datatype = li.get('data-type')
        if datatype is None and li.get_text().startswith("ニコニコ"):
            datatype = "nico"
        # content["video-details"][datatype] = li.get_text()
        if datatype == "nico":
            # "1話""最新話"
            content["video-details"][datatype] = li.get_text()[7:]
            content["video-details"][datatype] = []
            if "1話" in li.get_text():
                content["video-details"][datatype].append("first")
            if "最新話" in li.get_text():
                content["video-details"][datatype].append("newest")
        elif datatype == 'premium':
            content["video-details"][datatype] = li.get_text()
        elif datatype == 'danime':
            content["video-details"][datatype] = li.get_text()
        else:
            content["video-details"]["other"] = li.get_text()
    # {'class': 'J9hxP',
                       # 'ul': {'class': 'haPdW',
                              # 'li': [{'class': '_2ZVYy'},
                                     # {'class': '_2ZVYy',
                                      # 'data-type': 'premium'},
                                     # {'class': '_2ZVYy',
                                      # 'data-type': 'danime'}]}}
                                      # <li class="_2ZVYy">ニコニコ / 1話・最新話無料</li>
    
    content["content"] = base["content"].get_text()
    content["content"].replace('\u3000', '')
    return content
                

# @dataclasses.dataclass
# class NicoTitle:
    # pass
    


# 175-1rthzhecdme
   

            
# def get_timetable(count=1):
    
#     headers = {"authority": "gyao.yahoo.co.jp",
#                "referer": "https://gyao.yahoo.co.jp/schedule?category=anime"}

#     res = requests.get("https://gyao.yahoo.co.jp/api/schedule/anime?'", headers=headers)
#     if count:
#         d = res.json()
#         try:
#             assert(isinstance(d, dict))
#             assert(d["sections"][0]["items"])
#         except:
#             d = get_timetable(count-1)
#         return d
#     return None

# d = get_timetable(count=10)
# if d is None:
#     sys.exit(1)

# key = ["title", "id", "url"]
# ids = []
# title = []
# for day in d['sections']:
#     youbi = int(day["ult"]["pos"])
#     for item in day['items']:
#         item_d = {k: item[k] for k in key}
#         item_d["renew"] = []
#         item_d["renew"].append(youbi)
        
#         if item["id"] not in ids:
#             ids.append(item["id"])
#             title.append(item_d)
#         else:
#             i = ids.index(item["id"])
#             title[i]["renew"].append(youbi)
#             title[i]["renew"].sort()
            


# title.sort(key=itemgetter('id'))
# pprint(title)

# data_dir = Path("data", "gyao")
# # data_dir = "data/gyao"

# gyao_tt = Path('gyao_timetable.json')
# if gyao_tt.exists():
#     gyao_tt.unlink()

# # js_write(title, os.path.join(data_dir+"title.json"))
# if title:
#     js_write(title, data_dir / "title.json")
if __name__ == "__main__":
    t = get_abema_timetable02()
    split_abema_timetable02(t)
    
    year = 2023
    for season in range(0,4):
        try:
            n = NicoList(year, season)
            n.save()
        except:
            pass
            
    save_abema_allanime()
    
    
    
