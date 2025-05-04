import json
import time

import requests

import base64

import os

class FusionBrainAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_pipeline(self):
        response = requests.get(self.URL + 'key/api/v1/pipelines', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, pipeline, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'pipeline_id': (None, pipeline),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/pipeline/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/pipeline/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['result']['files']

            attempts -= 1
            time.sleep(delay)



def generate_im(promt):
    
    if not requests.get('http://ya.ru').ok:
        return False    
    
    api = FusionBrainAPI('https://api-key.fusionbrain.ai/', 'C8A1EB8D9FA2CFB74D636CB9190ACF67', 'F5DB158D51D97A34B5ED3F39786F3A3C')
    pipeline_id = api.get_pipeline()
    uuid = api.generate(prompt=promt, pipeline=pipeline_id)
    image_data = api.check_generation(uuid)[0]
    image_data = base64.b64decode(image_data)

    st = os.path.abspath('./images_for_txt_to_2d_generation/')
    
    try:
        with open(st + '\\tmp_image.jpg', mode='xb') as f:
            f.write(image_data)
            f.close()
        
        st = st + '\\tmp_image.jpg'

    except FileExistsError:
       
        i = 0
        while True:
            
            try:
                with open(st + f'\\tmp_image_{i}.jpg', mode='xb') as f:
                    f.write(image_data)
                    f.close()
                
                st = st + f'\\tmp_image_{i}.jpg'
                
                break
            
            except FileExistsError:
                i += 1
    
    return st