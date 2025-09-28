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

    def get_images_as_bytes(self, base64_strings):
        """
        Конвертирует base64 строки в bytes
        """
        images_bytes = []
        for base64_str in base64_strings:
            try:
                image_data = base64.b64decode(base64_str)
                images_bytes.append(image_data)
            except Exception as e:
                print(f"Ошибка декодирования: {e}")
        return images_bytes


# Измененная функция generate_image
def generate_image(prompt):
    api = FusionBrainAPI('https://api-key.fusionbrain.ai/', 'D2E7D31A8BB9A85A81D81CDA503F00E6', '85049FCF053B537DEA02BF956A63112D')
    pipeline_id = api.get_pipeline()
    uuid = api.generate(prompt, pipeline_id)
    base64_files = api.check_generation(uuid)
    
    if base64_files:
        images_bytes = api.get_images_as_bytes(base64_files)
        if images_bytes:
            return images_bytes[0], '.jpg'
    
    return None, None


if __name__ == '__main__':
    promt = """Ivan on the left and Anna on the right are sitting on a bench in a messy urban park. Ivan is pointing towards a pile of uncollected garbage bags near a playground. He looks upset.
    Appearance of left character:
A young man in his late 20s, named Ivan. He has short, slightly messy brown hair, wears a simple t-shirt and jeans. He looks confused and a bit frustrated at first, then engaged and happy.
Appearance of right character:
A young woman in her late 20s, named Anna. She has neat blonde hair tied in a ponytail, wears glasses and a smart casual blouse. She
looks knowledgeable, friendly, and helpful."""

    # Пример использования
    img_bytes, ext = generate_image(promt)
    if img_bytes:
        with open("generated_image.png", "wb") as f:
            f.write(img_bytes)
        print("Изображение сохранено как generated_image.png")