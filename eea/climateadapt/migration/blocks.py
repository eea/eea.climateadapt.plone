from .utils import make_uid


def make_title_block():
    uid = make_uid()
    block = {"@type": "title", "hideContentType": True}

    return [uid, block]
