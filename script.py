import requests
import json
import sys
from operator import itemgetter
from pathlib import Path
import os
from pprint import pprint

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
            
def get_timetable(count=1):
    
    headers = {"authority": "gyao.yahoo.co.jp",
               "referer": "https://gyao.yahoo.co.jp/schedule?category=anime"}

    res = requests.get("https://gyao.yahoo.co.jp/api/schedule/anime?'", headers=headers)
    if count:
        d = res.json()
        try:
            assert(isinstance(d, dict))
            assert(d["sections"][0]["items"])
        except:
            d = get_timetable(count-1)
        return d
    return None


d = get_timetable(count=10)
if d is None:
    sys.exit(1)

key = ["title", "id", "url"]
ids = []
title = []
for day in d['sections']:
    youbi = int(day["ult"]["pos"])
    for item in day['items']:
        item_d = {k: item[k] for k in key}
        item_d["renew"] = []
        item_d["renew"].append(youbi)
        
        if item["id"] not in ids:
            ids.append(item["id"])
            title.append(item_d)
        else:
            i = ids.index(item["id"])
            title[i]["renew"].append(youbi)
            title[i]["renew"].sort()
            


title.sort(key=itemgetter('id'))
pprint(title)

data_dir = Path("data", "gyao")
# data_dir = "data/gyao"

Path('gyao_timetable.json').unlink()

# js_write(title, os.path.join(data_dir+"title.json"))
if title:
    js_write(title, data_dir / "title.json")

