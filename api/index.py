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
    max_retries = 5
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
                p_values = []
                p_p = []
                text_values = []
                for d in root.findall('d'):
                    p, text = d.attrib['p'], d.text
                    p_values.append(float(p.split(',')[0]))
                    p_p.append(p)
                    text_values.append(text)
            
                # 对p的值进行排序并获取排序的索引
                sorted_indices = np.argsort(p_values)
            
                # 根据排序后的索引重新排列p的值和文本内容
                sorted_p_values = np.array(p_p)[sorted_indices]
                sorted_text_values = np.array(text_values)[sorted_indices]
                sorted_d_elements = list(zip(sorted_p_values, sorted_text_values))
                result = {
                    "code": 200,
                    "title": title,
                    "owner": owner,
                    "data": sorted_d_elements
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
