import base64
import json
import logging
import os
import requests
import time

from datetime import datetime
from requests.auth import HTTPDigestAuth
from zeep import Client
from zeep.wsse.username import UsernameToken

env = os.environ.get

ANNOTATION_KEY = "translation.cca.storage"
TRANS_USERNAME = "ipetchesi"  # TODO: get another username?
MARINE_PASS = env("MARINE_PASS", "")
SERVICE_URL = "https://webgate.ec.europa.eu/etranslation/si/translate"
site_url = "https://cca.devel5cph.eionet.europa.eu"

logger = logging.getLogger("eea.climateadapt")

# LOGFILE_NAME = "translate_{}.log".format(
#     datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
# logging.basicConfig(filename=LOGFILE_NAME, filemode='w',
#     format='%(levelname)s - %(message)s')

REQUEST = {
    "language": "de",  # do not use uppercase, it will fail on saving translations
    "uid": "",
    "limit": 10000,  # this is our default, as used in latest demo translations
    "offset": 0,
    "portal_type": "",
}


def get_translation_json_files(uid=None):
    json_files = []
    if uid:
        if os.path.exists("/tmp/jsons/" + str(uid) + ".json"):
            json_files.append(str(uid) + ".json")
    else:
        json_files = os.listdir("/tmp/jsons/")
    return json_files


def retrieve_translation(country_code, text, target_languages=None, force=False):
    """Send a call to automatic translation service, to translate a string
    Returns a json formatted string
    """

    dest = "{}/@@translate-callback?source_lang={}".format(
        site_url, country_code)

    # logger.warning('Translate callback URL: %s', dest)

    data = {
        "priority": 5,
        "callerInformation": {
            "application": "Marine_EEA_20180706",
            "username": TRANS_USERNAME,
        },
        "domain": "SPD",
        "externalReference": text,  # externalReference,
        "textToTranslate": text,
        "sourceLanguage": country_code,
        "targetLanguages": target_languages,
        "destinations": {
            "httpDestinations": [dest],
        },
    }

    logger.warning("Data translation request : %r", data)

    resp = requests.post(
        SERVICE_URL,
        auth=HTTPDigestAuth("Marine_EEA_20180706", MARINE_PASS),
        data=json.dumps(data),
        headers={"Content-Type": "application/json"},
    )
    logger.warning("Response from translation request: %r", resp.content)

    if isinstance(resp, int):
        if resp == int("-20028"):
            # 250 docs or 500 texts
            logger.error("LIMITS EXCEEDED, requests rejected by eTranslation")
            time.sleep(60)
            # import pdb; pdb.set_trace()

    res = {"transId": resp.content, "externalRefId": text}

    return res


def retrieve_html_translation(
    source_lang, html, obj_path, target_languages=None, force=False
):
    """Send a call to automatic translation service, to translate a string
    Returns a json formatted string
    """

    if not html:
        return

    if not target_languages:
        target_languages = ["EN"]

    encoded_html = base64.b64encode(html)

    client = Client(
        "https://webgate.ec.europa.eu/etranslation/si/WSEndpointHandlerService?WSDL",
        wsse=UsernameToken(TRANS_USERNAME, MARINE_PASS),
    )

    dest = "{}/@@translate-callback?source_lang={}&format=html".format(
        site_url, source_lang
    )

    resp = client.service.translate(
        {
            "priority": "5",
            "external-reference": obj_path,
            "caller-information": {
                "application": "Marine_EEA_20180706",
                "username": TRANS_USERNAME,
            },
            "document-to-translate-base64": {
                "content": encoded_html,
                "format": "html",
                "fileName": "out",
            },
            "source-language": source_lang,
            "target-languages": {"target-language": target_languages},
            "domain": "GEN",
            "output-format": "html",
            "destinations": {
                "http-destination": dest,
            },
        }
    )

    logger.warning("Data translation request : html content")
    logger.warning("Response from translation request: %r", resp)

    res = {"transId": resp, "externalRefId": html}

    return res


def translation_step_2(request=None):
    # bin/standalone run bin/run_translation_step_2

    if not request:
        # request_file = open('request.json')
        # REQUEST = json.load(request_file)
        # request_file.close()
        request = REQUEST

    language = request.get("language", None)
    uid = request.get("uid", None)
    limit = int(request.get("limit", 0))
    offset = int(request.get("offset", 0))
    portal_type = request.get("portal_type", None)

    logger.warning("Starting translation step 2 for language %s", language)

    """ Get all jsons objects in english and call etranslation for each field
        to be translated in specified language.
    """
    if language is None:
        return "Missing language parameter. (Example: ?language=it)"

    json_files = get_translation_json_files(uid)

    report_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report = {}
    report["date"] = {
        "start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "end": None,
    }
    report["filter"] = {
        "language": language,
        "uid": uid,
        "limit": limit,
        "offset": offset,
        "portal_type": portal_type,
    }
    error_report = {}
    # total translatable eng objects (not unique)
    total_files = len(json_files)
    nr_files = 0  # total translatable eng objects (not unique)
    nr_items = 0  # total translatable eng objects (not unique)
    nr_html_items = 0  # total translatable eng objects (not unique)
    nr_items_translated = 0  # found translated objects
    # import pdb; pdb.set_trace()
    if limit:
        json_files.sort()
        json_files = json_files[offset: offset + limit]

    for json_file in json_files:
        file = open("/tmp/jsons/" + json_file, "r")
        json_content = file.read()
        try:
            json_data = json.loads(json_content)
        except:
            error_report = {json_file: "Error in json file"}
            json_object = json.dumps(error_report, indent=4)
            with open(
                "/tmp/errors_step_2_" + language + "_" + report_date + ".json", "w"
            ) as outfile:
                outfile.write(json_object)

            continue
        if portal_type and portal_type != json_data["portal_type"]:
            continue
        nr_files += 1
        # LOPP object tiles
        tile_html_fields = []
        if "tile" in json_data:
            for tile_id in list(json_data["tile"].keys()):
                tile_data = json_data["tile"][tile_id]
                # LOOP tile text items
                for key in list(tile_data["item"].keys()):
                    res = retrieve_translation(
                        "EN", tile_data["item"][key], [language.upper()]
                    )
                    nr_items += 1
                    if "translated" in res:
                        nr_items_translated += 1
                # LOOP tile HTML items
                for key in list(tile_data["html"].keys()):
                    value = tile_data["html"][key]
                    value = value.replace("\r", "")
                    value = value.replace("\n", "")
                    try:
                        test_value = value + "test"
                    except UnicodeDecodeError:
                        value = value.decode("utf-8")
                    tile_html_fields.append(
                        {"tile_id": tile_id, "field": key, "value": value}
                    )

        # TILE HTML fields translate in one call
        if len(tile_html_fields):
            nr_html_items += 1
            trans_obj_path = json_data.get("translated_obj_paths", {}).get(
                language, None
            )
            if not trans_obj_path:
                continue
            html_content = "<!doctype html>" + "<head><meta charset=utf-8></head><body>"
            for item in tile_html_fields:
                html_tile = (
                    "<div class='cca-translation-tile'"
                    + " data-field='"
                    + item["field"]
                    + "'"
                    + " data-tile-id='"
                    + item["tile_id"]
                    + "'"
                    + ">"
                    + item["value"]
                    + "</div>"
                )
                html_content += html_tile

            html_content += "</body></html>"
            html_content = html_content.encode("utf-8")
            translated = retrieve_html_translation(
                "EN",
                html_content,
                trans_obj_path,
                language.upper(),
            )

        # LOOP object text items
        for key in list(json_data["item"].keys()):
            res = retrieve_translation(
                "EN", json_data["item"][key], [language.upper()])
            nr_items += 1
            if "translated" in res:
                nr_items_translated += 1

        # LOOP object HTML items
        if len(json_data["html"]):
            nr_html_items += 1
            trans_obj_path = json_data.get("translated_obj_paths", {}).get(
                language, None
            )
            if not trans_obj_path:
                continue

            html_content = "<!doctype html><head><meta charset=utf-8></head>"
            html_content += "<body>"

            for key in list(json_data["html"].keys()):
                value = json_data["html"][key].replace("\r\n", "")
                html_section = (
                    "<div class='cca-translation-section'"
                    + " data-field='"
                    + key
                    + "'>"
                    + value
                    + "</div>"
                )

                html_content += html_section

            html_content += "</body></html>"
            html_content = html_content.encode("utf-8")
            res = retrieve_html_translation(
                "EN",
                html_content,
                trans_obj_path,
                language.upper(),
                False,
            )

        logger.warning(
            "TransStep2 File  %s from %s, total files %s",
            nr_files,
            len(json_files),
            total_files,
        )
        report["date"]["last_update"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S")
        report["response"] = {
            "items": {
                "nr_files": nr_files,
                "nr": nr_items,
                "nr_already_translated": nr_items_translated,
            },
            "htmls": nr_html_items,
            "portal_type": portal_type,
        }
        report["total_files"] = total_files
        report["status"] = "Processing"

        json_object = json.dumps(report, indent=4)
        with open(
            "/tmp/translate_step_2_" + language + "_" + report_date + ".json", "w"
        ) as outfile:
            outfile.write(json_object)
        time.sleep(0.2)

    report["date"]["end"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report["status"] = "Done"
    report["response"] = {
        "items": {
            "nr_files": nr_files,
            "nr": nr_items,
            "nr_already_translated": nr_items_translated,
        },
        "htmls": nr_html_items,
        "portal_type": portal_type,
    }
    report["total_files"] = total_files

    json_object = json.dumps(report, indent=4)
    with open(
        "/tmp/translate_step_2_" + language + "_" + report_date + ".json", "w"
    ) as outfile:
        outfile.write(json_object)

    error_json_object = json.dumps(error_report, indent=4)
    with open(
        "/tmp/errors_step_2_" + language + "_" + report_date + ".json", "w"
    ) as outfile:
        outfile.write(error_json_object)

    logger.warning(
        "Files: %s, TotalItems: %s, Already translated: %s HtmlItems: %s",
        nr_files,
        nr_items,
        nr_items_translated,
        nr_html_items,
    )


if __name__ == "__main__":
    import sys
    from os import path, listdir

    sys.path.append(path.dirname(path.dirname(
        path.dirname(path.abspath(__file__)))))
    # sys.path.append('/plone/instance/src/plone.app.multilingual/src/plone/app/multilingual')
    sys.path.append("/plone/buildout-cache/eggs/attrs-19.3.0-py2.7.egg/attr")

    eggs_path = "/plone/buildout-cache/eggs"
    eggs = listdir(eggs_path)

    for egg in eggs:
        sys.path.append(path.join(eggs_path, egg))

    translation_step_2(REQUEST)
