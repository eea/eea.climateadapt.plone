import logging

import json
import urllib.request

from plone.restapi.interfaces import IExpandableElement, ISerializeToJson
from zope.component import adapter, queryMultiAdapter
from zope.interface import Interface, implementer

from eea.climateadapt.behaviors.mission_signatory_profile import (
    IMissionSignatoryProfile,
)
# from pkg_resources import resource_filename
# import csv

logger = logging.getLogger("eea.climateadapt")


DISCODATA_URLS = {
    "governance": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%205000%20*%20FROM%20%5BMissionOnAdaptation%5D.%5Blatest%5D.%5Bv_Governance_Template_Text%5D&p=1&nrOfHits=5000",
    "assessment_text": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%205000%20*%20FROM%20%5BMissionOnAdaptation%5D.%5Blatest%5D.%5Bv_Assessment_Template_Text%5D&p=1&nrOfHits=5000",
    "assessment_factors": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%205000%20*%20FROM%20%5BMissionOnAdaptation%5D.%5Blatest%5D.%5Bv_Assessment_Template_Factors_Text%5D&p=1&nrOfHits=5000",
    "assessment_risks": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%205000%20*%20FROM%20%5BMissionOnAdaptation%5D.%5Blatest%5D.%5Bv_Assessment_Template_Climate_Risk_Assessments_Text%5D&p=1&nrOfHits=5000",
    "assessment_hazards_sectors": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%205000%20*%20FROM%20%5BMissionOnAdaptation%5D.%5Blatest%5D.%5Bv_Assessment_Template_Hazards_Sectors_Text%5D&p=1&nrOfHits=5000",
    "action_text": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%205000%20*%20FROM%20%5BMissionOnAdaptation%5D.%5Blatest%5D.%5Bv_Action_Template_Text%5D&p=1&nrOfHits=5000",
    "action_actions": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%205000%20*%20FROM%20%5BMissionOnAdaptation%5D.%5Blatest%5D.%5Bv_Action_Template_Actions_Text%5D&p=1&nrOfHits=5000",
    "action_hazards": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%205000%20*%20FROM%20%5BMissionOnAdaptation%5D.%5Blatest%5D.%5Bv_Action_Template_Climate_Hazards_Text%5D&p=1&nrOfHits=5000",
    "action_sectors": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%205000%20*%20FROM%20%5BMissionOnAdaptation%5D.%5Blatest%5D.%5Bv_Action_Template_Sectors_Text%5D&p=1&nrOfHits=5000",
    "action_benefits": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%205000%20*%20FROM%20%5BMissionOnAdaptation%5D.%5Blatest%5D.%5Bv_Action_Template_Co_Benefits_Text%5D&p=1&nrOfHits=5000",
    "planning_titles": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%205000%20*%20FROM%20%5BMissionOnAdaptation%5D.%5Blatest%5D.%5Bv_Planning_Template_Adaptation_Text%5D&p=1&nrOfHits=5000",
    "planning_goals": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%205000%20*%20FROM%20%5BMissionOnAdaptation%5D.%5Blatest%5D.%5Bv_Planning_Template_Adaptation_Goals_Text%5D&p=1&nrOfHits=5000",
    "planning_goals_hazard": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%205000%20*%20FROM%20%5BMissionOnAdaptation%5D.%5Blatest%5D.%5Bv_Planning_Template_Adaptation_Goals_Climate_Hazards_Text%5D&p=1&nrOfHits=5000",
    "planning_climate_action": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%205000%20*%20FROM%20%5BMissionOnAdaptation%5D.%5Blatest%5D.%5Bv_Planning_Template_Climate_Action_Plan_Text%5D&p=1&nrOfHits=5000",
    "planning_climate_action_sectors": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%205000%20*%20FROM%20%5BMissionOnAdaptation%5D.%5Blatest%5D.%5Bv_Planning_Template_Climate_Action_Plan_Sectors_Text%5D&p=1&nrOfHits=5000",
    "tabs_labels": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%205000%20*%20FROM%20%5BMissionOnAdaptation%5D.%5Blatest%5D.%5Bv_Tabs_Text%5D&p=1&nrOfHits=5000",
    "footer_text": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%205000%20*%20FROM%20%5BMissionOnAdaptation%5D.%5Blatest%5D.%5Bv_Footer_Text%5D&p=1&nrOfHits=5000",
    "general_text": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%205000%20*%20FROM%20%5BMissionOnAdaptation%5D.%5Blatest%5D.%5Bv_General_Text%5D&p=1&nrOfHits=5000",
}

DISCODATA_BETA_URLS = {
    key: url.replace("latest", "v2").replace("MissionOnAdaptation", "MissionOnAdaptation_SignatoryReporting")
    for key, url in DISCODATA_URLS.items()
}

SIGN_PROFILE_HEADER_IMAGE_PATH = "/cca/en/mission/sig-profile-header.jpeg"


def fetch_discodata_json(url):
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode()).get("results", [])
    except Exception as e:
        logger.error(f"[DISCODATA] Failed to fetch or parse JSON from {url}: {e}")
        return []


def filter_by_profile_id(data, profile_id):
    return [row for row in data if str(row.get("Id")) == str(profile_id)]


def build_map(data, id_keys, value_key):
    result = {}
    for row in data:
        key = tuple(row.get(k) for k in id_keys)
        result.setdefault(key, []).append(row.get(value_key))
    return result

def build_map_objects(data, id_keys, fields):
    result = {}
    for row in data:
        key = tuple(row.get(k) for k in id_keys)
        value = {field: row.get(field) for field in fields}
        result.setdefault(key, []).append(value)
    return result

# def parse_csv(path):
#     try:
#         wf = resource_filename("eea.climateadapt", path)
#         with open(wf, newline="", encoding="utf-8-sig") as csvfile:
#             reader = csv.DictReader(csvfile)
#             # print(f"Headers: {reader.fieldnames}")
#             return [row for row in reader]
#     except Exception as e:
#         logger.error(f"Failed to parse CSV {path}: {e}")
#         return []


def get_planning_data(profile_id, data):
    planning_goals = filter_by_profile_id(
        fetch_discodata_json(data["planning_goals"]), profile_id
    )
    hazards_map = build_map(
        fetch_discodata_json(data["planning_goals_hazard"]),
        ["Id", "Adaptation_Goal_Id"],
        "Climate_Hazard",
    )

    planning_climate_action = filter_by_profile_id(
        fetch_discodata_json(data["planning_climate_action"]), profile_id
    )
    sectors_map = build_map_objects(
        fetch_discodata_json(data["planning_climate_action_sectors"]),
        ["Id", "Climate_Action_Plan_Id"],
        ["Sector", "Icon"]
    )

    for row in planning_goals:
        key = (row.get("Id"), row.get("Adaptation_Goal_Id"))
        row["Climate_Hazards"] = hazards_map.get(key, [])

    for row in planning_climate_action:
        key = (row.get("Id"), row.get("Climate_Action_Plan_Id"))
        row["Sectors"] = sectors_map.get(key, [])

    return {
        "planning": {
            "planning_titles": filter_by_profile_id(
                fetch_discodata_json(data["planning_titles"]), profile_id
            ),
            "planning_goals": planning_goals,
            "planning_climate_action": planning_climate_action,
        }
    }


def get_assessment_data(profile_id, data):
    assessment_hazards_sectors_raw = filter_by_profile_id(
        fetch_discodata_json(data["assessment_hazards_sectors"]), profile_id
    )

    grouped = {}
    for row in assessment_hazards_sectors_raw:
        key = (row.get("Hazard_Id"), row.get("Hazard"))
        sector = row.get("Sector")
        order = int(row.get("Order", 999))
        if key not in grouped:
            grouped[key] = []
        grouped[key].append((order, sector))

    assessment_hazards_sectors = []
    for (hazard_id, hazard), sectors in grouped.items():
        sorted_sectors = [
            sector for order, sector in sorted(sectors, key=lambda x: x[0])
        ]
        assessment_hazards_sectors.append(
            {
                "Hazard_Id": hazard_id,
                "Hazard": hazard,
                "Sectors": sorted_sectors,
            }
        )

    return {
        "assessment": {
            "assessment_text": filter_by_profile_id(
                fetch_discodata_json(data["assessment_text"]), profile_id
            ),
            "assessment_factors": filter_by_profile_id(
                fetch_discodata_json(data["assessment_factors"]), profile_id
            ),
            "assessment_risks": filter_by_profile_id(
                fetch_discodata_json(data["assessment_risks"]), profile_id
            ),
            "assessment_hazards_sectors": assessment_hazards_sectors,
        }
    }


def get_action_data(profile_id, data):
    actions = filter_by_profile_id(
        fetch_discodata_json(data["action_actions"]), profile_id
    )
    hazards_map = build_map(
        fetch_discodata_json(data["action_hazards"]),
        ["Id", "Action_Id"],
        "Climate_Hazard",
    )
    sectors_map = build_map_objects(
        fetch_discodata_json(data["action_sectors"]),
        ["Id", "Action_Id"],
        ["Sector", "Icon"]
    )
    benefits_map = build_map(
        fetch_discodata_json(data["action_benefits"]),
        ["Id", "Action_Id"],
        "Co_Benefit",
    )

    for row in actions:
        key = (row.get("Id"), row.get("Action_Id"))
        row["Climate_Hazards"] = hazards_map.get(key, [])
        row["Sectors"] = sectors_map.get(key, [])
        row["Co_Benefits"] = benefits_map.get(key, [])

    return {
        "action": {
            "action_text": filter_by_profile_id(
                fetch_discodata_json(data["action_text"]), profile_id
            ),
            "actions": actions,
        }
    }


def get_governance_data(profile_id, data):
    data = fetch_discodata_json(data["governance"])
    return {"governance": filter_by_profile_id(data, profile_id)}


def get_general_text_data(profile_id, data):
    data = fetch_discodata_json(data["general_text"])
    return {"general_text": filter_by_profile_id(data, profile_id)}


def get_tab_labels_data(_, data):
    try:
        rows = fetch_discodata_json(data["tabs_labels"])
        if rows:
            first_row = rows[0]

            # Preserve order as defined by SQL column order
            tab_labels = [{"key": key, "value": first_row[key]} for key in first_row]

            return {"tab_labels": tab_labels}
        return {}
    except Exception as e:
        logger.error(f"Failed to process tab labels: {e}")
        return {}


def get_footer_text_data(_, data):
    data = fetch_discodata_json(data["footer_text"])
    return {"footer_text": data[0]} if data else {}


def get_data_for_mission_signatory(profile_id, data=DISCODATA_URLS):
    """Fetches data from DISCODATA."""
    data_sections = [
        get_governance_data,
        get_planning_data,
        get_assessment_data,
        get_action_data,
        get_general_text_data,
        get_tab_labels_data,
        get_footer_text_data,
    ]
    result = {}

    for section in data_sections:
        try:
            result.update(section(profile_id, data))
        except Exception as e:
            logger.warning(f"[Data Fetch] Failed: {e}")
    return result


@implementer(IExpandableElement)
@adapter(IMissionSignatoryProfile, Interface)
class MissionSignatoryProfile(object):
    """An expander that inserts the data of a mission signatory profile"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        profile_id = self.context.absolute_url().rstrip("/").split("/")[-1]
        data = get_data_for_mission_signatory(profile_id, DISCODATA_URLS)
        data_beta = get_data_for_mission_signatory(profile_id, DISCODATA_BETA_URLS)

        banner = None
        try:
            banner = self.context.restrictedTraverse(SIGN_PROFILE_HEADER_IMAGE_PATH)
        except Exception:
            logger.warning("Could not find signatory profile banner image")
            pass

        if banner is not None:
            serializer = queryMultiAdapter((banner, self.request), ISerializeToJson)
            data["image"] = serializer()["image"]
            data_beta["image"] = serializer()["image"]


        result = {
            "missionsignatoryprofile": {
                "@id": "{}/@missionsignatoryprofile".format(
                    self.context.absolute_url()
                ),
                "result": data,
                "result_beta": data_beta,
            }
        }

        return result
