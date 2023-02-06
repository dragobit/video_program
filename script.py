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
        j = {"pubAt": t.publishedAt, "pubDate": fromtimestamp(t.publishedAt).strftime("%Y%m%d%H"),"slots":[]}
        j["slots"] = v
        timetable_path = Fold.abema_tt/ "part"/ f"{k}.json"
        timetable_path.parent.mkdir(exist_ok=True, parents=True)
        if timetable_path.exists():
            j2 = js_open(timetable_path)
            if j["slots"] != j2["slots"]:
                js_write(j, timetable_path)
        else:
            js_write(j, timetable_path)

       
# get_abema_timetable() 
if __name__ == "__main__":
    t = get_abema_timetable02()
    split_abema_timetable(t)

   

            
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

