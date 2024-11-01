"""Init"""

import logging
from datetime import datetime

from langdetect import detect
from persistent import Persistent

ANNOTATION_KEY = "translation.cca.storage"

logger = logging.getLogger("wise.msfd.translation")


def get_detected_lang(text):
    """Detect the language of the text, return None for short texts"""

    if len(text) < 50:
        return None

    try:
        detect_lang = detect(text)
    except Exception:
        # Can't detect language if text is an url
        # it throws LangDetectException
        return None

    return detect_lang


class Translation(Persistent):
    def __init__(self, text, source=None):
        self.text = text
        self.source = source
        self.approved = False
        self.modified = datetime.now()

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.text


def normalize(text):
    if not isinstance(text, basestring):
        return text

    if isinstance(text, str):
        text = text.decode("utf-8")

    if not text:
        return text

    text = text.strip().replace("\r\n", "\n").replace("\r", "\n")

    return text
