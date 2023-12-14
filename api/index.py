from flask import Flask, request
import json
import requests
import time

app = Flask(__name__)

@app.route('/')
def home():
    bv = request.args.get('bv')
    p = request.args.get('p', default= 1, type=int)
    url = 'https://api.bilibili.com/x/web-interface/view/detail'
    params = {'bvid': bv}
    max_retries = 5
    retry_count = 0
    while retry_count < max_retries:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            json_data = response.json()
            cid = json_data["data"]["View"]["pages"][p-1]["cid"]
            print(cid)
            return f"{cid}. Status code: {response.status_code}"
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}. Retrying...")
            retry_count += 1
            time.sleep(1)  # 
    if retry_count == max_retries:
        return f"Failed to fetch data. Status code: {response.status_code}"
    

@app.route('/about')
def about():
    return 'About'
