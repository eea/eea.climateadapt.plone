from uuid import uuid4
import json
import logging
import requests

SLATE_CONVERTER = "http://converter:8000/html"
BLOCKS_CONVERTER = "http://converter:8000/toblocks"

logger = logging.getLogger("eea.climateadapt")


def path(obj):
    return "/" + "/".join(obj.absolute_url(relative=1).split("/")[2:])


def convert_to_blocks(text):
    data = {"html": text}
    headers = {"Content-type": "application/json",
               "Accept": "application/json"}

    req = requests.post(
        BLOCKS_CONVERTER, data=json.dumps(data), headers=headers)
    if req.status_code != 200:
        logger.debug(req.text)
        raise ValueError

    blocks = req.json()["data"]
    return blocks


def text_to_slate(text):
    data = {"html": text}
    headers = {"Content-type": "application/json",
               "Accept": "application/json"}

    req = requests.post(
        SLATE_CONVERTER, data=json.dumps(data), headers=headers)
    slate = req.json()["data"]
    return slate


def convert_block(block):
    # TODO: do the plaintext
    return {"@type": "slate", "value": [block], "plaintext": ""}


def slate_to_blocks(slate):
    blocks = [[str(uuid4()), convert_block(block)] for block in slate]
    return blocks


def make_uid():
    return str(uuid4())
