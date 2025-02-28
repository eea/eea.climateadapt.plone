import redis
import json

from eea.climateadapt.callbackdatamanager import queue_callback


def queue_job(queue_name, job_name, data, opts=None):
    opts = opts or {
        "delay": 0,  # Delay in milliseconds
        "priority": 1,
        "attempts": 3,
    }

    job_data = {
        "name": job_name,
        "data": data,
        "opts": opts,
    }

    r = redis.Redis(host="localhost", port=6379, db=0)
    data = json.dumps(job_data)

    def callback():
        r.lpush(queue_name, data)

    queue_callback(callback)

    print(f"Job added to queue: {queue_name}")


def queue_translate_volto_html(url, html, language=None):
    """The "new" method of triggering the translation of an object.

    While this is named "volto", it is a generic system to translate Plone
    content. The actual "ingestion" of translated data is performed in the
    TranslationCallback view

    Input: html (generated from volto blocks and obj fields, as string)
           en_obj - the object to be translated
           http_host - website url

    Makes sure translation objects exists and requests a translation for
    all languages.
    """

    data = {
        "obj_url": url,
        "html_content": html,
    }

    logger.info("Called translate_volto_html for %s", url)
    languages = language and [language] or []  # get_site_languages()

    if "cca/en" in url:
        for language in languages:  # temporary
            if language == "en":
                continue

            queue_job("etranslation", "call_etranslation", data)
