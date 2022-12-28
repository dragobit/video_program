import requests
import json
import sys
from operator import itemgetter
from pathlib import Path
import os

def js_open(js):
    if isinstance(js, (str, Path)):
        with open(js,'rt') as f:#, errors='ignore',encoding='unicode-escape'
            D1 = json.load(f)#object_pairs_hook=OrderedDict 
    return D1

def js_write(dic, js):
    if isinstance(js, (str, Path)):
        with open(js, 'w') as f:
            json.dump(dic, f,indent=4, ensure_ascii=False)

res = requests.get("https://gyao.yahoo.co.jp/api/schedule/anime?'")
d = res.json()
try:
    assert(isinstance(d, dict))
except:
    sys.exit(1)

key = ["title", "id", "url"]
title = []
for day in d['sections']:
    for item in day['items']:
        item_d = {k: item[k] for k in key}
        if item_d not in title:
            title.append(item_d)

title.sort(key=itemgetter('id'))

data_dir = Path("data", "gyao")
# data_dir = "data/gyao"

# js_write(title, os.path.join(data_dir+"title.json"))
js_write(title, data_dir / "title.json")

