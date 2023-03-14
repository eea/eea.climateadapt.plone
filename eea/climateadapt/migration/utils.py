import json
from uuid import uuid4

import requests

CONVERTER = "http://converter:8000/html"


def text_to_slate(text):
    data = {"html": text}
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

    req = requests.post(CONVERTER, data=json.dumps(data), headers=headers)
    slate = req.json()['data']
    return slate


def convert_block(block):
    # TODO: do the plaintext
    return {"@type": "slate", "value": [block], "plaintext": ""}


def slate_to_blocks(slate):
    blocks = [[str(uuid4()), convert_block(block)] for block in slate]
    return blocks
