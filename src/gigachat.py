
# D2E7D31A8BB9A85A81D81CDA503F00E6
# 85049FCF053B537DEA02BF956A63112D

import json
import time

import base64
import requests


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

    def generate(self, promt, pipeline_id, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "style": "DIGITAL ART",
            "generateParams": {
                "query": promt
            }
        }

        data = {
            'pipeline_id': (None, pipeline_id),
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

    def save_base64_image(self, base64_string, filename="generated_image.png"):
        try:
            # Декодируем Base64 в байты
            image_data = base64.b64decode(base64_string)
            
            # Сохраняем в файл
            with open(filename, "wb") as f:
                f.write(image_data)
            
            print(f"Изображение сохранено как: {filename}")
            return True
        except Exception as e:
            print(f"Ошибка: {e}")
            return False

if __name__ == '__main__':

    promt = """Ivan on the left and Anna on the right are sitting on a bench in a messy urban park. Ivan is pointing towards a pile of uncollected garbage bags near a playground. He looks upset.
    Appearance of left character:
A young man in his late 20s, named Ivan. He has short, slightly messy brown hair, wears a simple t-shirt and jeans. He looks confused and a bit frustrated at first, then engaged and happy.
Appearance of right character:
A young woman in her late 20s, named Anna. She has neat blonde hair tied in a ponytail, wears glasses and a smart casual blouse. She
looks knowledgeable, friendly, and helpful."""

    api = FusionBrainAPI('https://api-key.fusionbrain.ai/', 'D2E7D31A8BB9A85A81D81CDA503F00E6', '85049FCF053B537DEA02BF956A63112D')
    pipeline_id = api.get_pipeline()
    uuid = api.generate(promt, pipeline_id)
    files = api.check_generation(uuid)

    for i, base64_img in enumerate(files):
        api.save_base64_image(base64_img, f"my_image_{i}.png")

#Не забудьте указать именно ваш YOUR_KEY и YOUR_SECRET.
