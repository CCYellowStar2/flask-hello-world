from flask import Flask, request
import json
import requests
import time
import xml.etree.ElementTree as ET
import numpy as np

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
    
    while retry_count < max_retries:
        if not cid:
            response = requests.get(url, params=params)
        
        if cid or response.status_code == 200:
            if not cid:
                json_data = response.json()
                title= json_data["data"]["View"]["title"]
                owner= json_data["data"]["View"]["owner"]["name"]
                cid = json_data["data"]["View"]["pages"][p-1]["cid"]
                print(cid)
            url2= f"https://comment.bilibili.com/{cid}.xml"
            response2 = requests.get(url2)
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
                result = {
                    "code": 200,
                    "title": title,
                    "owner": owner,
                    "data": sorted_entries.tolist()
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
    

@app.route('/about')
def about():
    return 'About'
