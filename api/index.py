from flask import Flask, request
import json
import requests
import time
import xml.etree.ElementTree as ET

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
    
    while retry_count < max_retries:
        if not cid:
            response = requests.get(url, params=params)
        
        if cid or response.status_code == 200:
            if not cid:
                json_data = response.json()
                cid = json_data["data"]["View"]["pages"][p-1]["cid"]
                print(cid)
            url2= f"https://comment.bilibili.com/{cid}.xml"
            response2 = requests.get(url2)
            if response2.status_code == 200:
                root = ET.fromstring(response2.content)
                for d in root.findall('d'):
                    p_value = d.attrib['p']
                    text = d.text                
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
