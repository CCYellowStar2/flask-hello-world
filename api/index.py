from flask import Flask, request
import json
import requests
import time
import xml.etree.ElementTree as ET
import numpy as np
import random

headers = {
    "cookie": "buvid4=9D715CF5-4326-1CB0-134C-10363A1F230344345-022060710-3RZtRYV5AZewWHGrlokJoQ%3D%3D; buvid3=FD39475C-DA34-2D57-CACA-CD2D5A064B4956972infoc; b_nut=1702722756; i-wanna-go-back=-1; b_ut=7; _uuid=FF212E33-4DA7-FECE-72C3-EF10102529471745090infoc; enable_web_push=DISABLE; header_theme_version=CLOSE; DedeUserID=350809631; DedeUserID__ckMd5=5c596f5bf64d5d39; fingerprint=f8d0c1f49bd56bbdff8c6350e92c5bc6; buvid_fp_plain=undefined; CURRENT_FNVAL=16; buvid_fp=f8d0c1f49bd56bbdff8c6350e92c5bc6; rpdid=|(~J|~Ylm)m0J'u~|k~JJY~Y; is-2022-channel=1; SESSDATA=5180a568%2C1720445034%2Cd1d9f%2A11CjAurlX0w_bgK4az7B9NN-azs4e3paMHJrIxs3T9sWoInZnpVhCuI2VeiI8NvbXqBkMSVndMdWU0b1BiQlAyMlZyWVN4aE5LYXhVa0E3eU9SekFIekc5N1pBMlFOWldZb1Y2b2JYODc2Vzd5S2ZpaFpvVmZFRm9TcnRrRHZPTUFIdnJNcHJsNmJ3IIEC; bili_jct=1c50da6232bab24d77c175a8a2a5eccc; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDUxNTM3MDYsImlhdCI6MTcwNDg5NDQ0NiwicGx0IjotMX0.Y_H66jTwbCpUQiSXqosjRjr3ysWVzYl7H9-VUcJC8Xc; bili_ticket_expires=1705153646; innersign=0; b_lsid=17DB9591_18CF3A4A1C5; bmg_af_switch=1; bmg_src_def_domain=i2.hdslb.com; sid=nb8h34j5; home_feed_column=4; browser_resolution=795-966; PVID=2",
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
    url = f'https://api.bilibili.com/x/web-interface/index/top/rcmd'
    response = requests.get(url, headers=headers)
    json_data = response.json()
    return json_data
