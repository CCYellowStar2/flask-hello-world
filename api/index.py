from flask import Flask, request
import json
import requests
import time
import xml.etree.ElementTree as ET
import numpy as np
import random

headers = {
    "cookie": "b_nut=1693047061; buvid3=D9E5F588-B16D-452B-CBDA-E3B57976FB5561563infoc; CURRENT_FNVAL=4048; _uuid=8D3D7BCB-CD21-5B9B-39FD-F4F235DC110A562397infoc; buvid4=4DEFB59D-A5DB-972B-5144-02D8BEAEC1C562418-023082618-9TO+hWhxQHNfJ9z+aPycsm9q2KEgbcCzj6FRB8EdS1WAC29XPiIPEQ==; rpdid=0zbfAHJoFj|bFx94ZSH|1Lq|3w1QzQSI; header_theme_version=CLOSE; home_feed_column=5; LIVE_BUVID=AUTO2616930471075890; CURRENT_QUALITY=116; fingerprint=5e0b6903dd2a13587cc7205519b5b372; buvid_fp_plain=undefined; buvid_fp=5e0b6903dd2a13587cc7205519b5b372; innersign=0; b_lsid=8110F18BD_18D0309416F; bmg_af_switch=1; bmg_src_def_domain=i2.hdslb.com; enable_web_push=DISABLE; bp_video_offset_35033095=886113484750716928; SESSDATA=5d4c5473,1720705091,6e1ea*12CjBEmByHNrBvi_W6Ex_suGmcddrawbVQ1akCKvgbhbg6ltFeh2NafzVjdh6shyXOPQUSVk44YUk1c010TkZZdXZSVGNfd1ZicDJaTVUtajQ4VDdIWDBWMHRGd3lrcEtXNTA1YUt5T1FuU0Z5VEhiSDhkV0VFWEZLY3MzY3EwaEtBbmhWZEFqNFZnIIEC; bili_jct=33e208ca79e1d145fb5ea5d085b56314; DedeUserID=350809631; DedeUserID__ckMd5=5c596f5bf64d5d39; sid=7xgq4ccc; browser_resolution=1494-1138; PVID=1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35",
}
    
app = Flask(__name__)

@app.route('/')
def home():
    bv = request.args.get('bv')
    p = request.args.get('p', default= 1, type=int)
    url = 'https://api.bilibili.com/x/web-interface/view/detail'
    params = {'bvid': bv}
    max_retries = 10
    retry_count = 0
    cid=""
    title=""
    owner=""
    page=[]
    
    while retry_count < max_retries:
        if not cid:
            response = requests.get(url, params=params, headers=headers)
        
        if cid or response.status_code == 200:
            if not cid:
                json_data = response.json()
                title= json_data["data"]["View"]["title"]
                owner= json_data["data"]["View"]["owner"]["name"]
                cid = json_data["data"]["View"]["pages"][int(p)-1]["cid"]
                page = json_data["data"]["View"]["pages"]
                print(cid)
            url2= f"https://comment.bilibili.com/{cid}.xml"
            response2 = requests.get(url2, headers=headers)
            if response2.status_code == 200:
                root = ET.fromstring(response2.content)
                # 为每个条目创建一个特征元组，包括p和文本值
                entries = [(d.attrib['p'], d.text) for d in root.findall('d')]
            
                # 提取每个条目的第一个和第二个逗号前的数字
                p_values = np.array([entry[0] for entry in entries])
                first_comma_values = np.array([float(p.split(',')[0]) for p in p_values])
                second_comma_values = np.array([float(p.split(',')[1]) for p in p_values])
            
                # 对于相同的第一个逗号前的数字，按照第二个逗号前的数字排序
                sorted_indices = np.lexsort((second_comma_values, first_comma_values))
            
                # 输出排序后的结果
                sorted_entries = np.array(entries)[sorted_indices]
                comments_list = [{"info": comment[0], "text": comment[1].replace("[", "（").replace("]", "）").replace("［", "（").replace("］", "）")} for comment in sorted_entries]
                result = {
                    "code": 200,
                    "title": title,
                    "owner": owner,
                    "bv": bv,
                    "p": str(p),
                    "data": comments_list,
                    "pages": page
                }
                json_data2 = json.dumps(result, ensure_ascii=False)
                return json_data2
            else:
                print(f"Failed to fetch data. Status code: {response2.status_code}. Retrying...")
                retry_count += 1
                time.sleep(1)  
            break
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}. Retrying...")
            retry_count += 1
            time.sleep(1)  
    if retry_count == max_retries:
        return f"Failed to fetch data. Status code: {response.status_code}"

@app.route('/live')
def live():
    id = request.args.get('id')
    url = f'https://api.live.bilibili.com/room/v1/Room/get_info?room_id={id}'
    response = requests.get(url, headers=headers)
    json_data = response.json()
    uid = json_data["data"]["uid"]
    url2 = f"https://api.live.bilibili.com/live_user/v1/Master/info?uid={uid}"
    response2 = requests.get(url2, headers=headers)
    json_data2 = response2.json()
    uname = json_data2["data"]["info"]["uname"]
        # 在原始JSON中插入新的键值对
    json_data["data"]["uname"] = uname

    return json_data

@app.route('/search')
def search():
    keyword = request.args.get('keyword')
    page = request.args.get('page', default= "1")
    url = f'https://api.bilibili.com/x/web-interface/wbi/search/all/v2?keyword={keyword}&page={page}'
    response = requests.get(url, headers=headers)
    json_data = response.json()
    return json_data

@app.route('/live/search')
def livesearch():
    keyword = request.args.get('keyword')
    page = request.args.get('page', default= "1")
    url = f'https://api.bilibili.com/x/web-interface/wbi/search/type?search_type=live_room&keyword={keyword}&page={page}'
    response = requests.get(url, headers=headers)
    json_data = response.json()
    return json_data

@app.route('/index')
def index():
    page = request.args.get('page', default= "1")
    url = f'https://api.bilibili.com/x/web-interface/index/top/rcmd?ps=14&version=1'
    response = requests.get(url, headers=headers)
    json_data = response.json()
    return json_data
