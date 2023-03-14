import json

import requests

CONVERTER = "http://converter:8000/html"


def text_to_slate(text):
    data = {"html": text}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

    req = requests.post(CONVERTER, data=json.dumps(data), headers=headers)
    slate = req.json()['data']
    return slate


def slate_to_blocks(slate):
    return []
