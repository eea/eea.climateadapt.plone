import logging
import csv

import json
import urllib.request

from pkg_resources import resource_filename
from plone.restapi.interfaces import IExpandableElement
from zope.component import adapter
from zope.interface import Interface, implementer

from eea.climateadapt.behaviors.mission_signatory_profile import (
    IMissionSignatoryProfile,
)

logger = logging.getLogger("eea.climateadapt")


DISCODATA_URLS = {
    "governance": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%201000%20*%20FROM%20[MissionOnAdaptation].[latest].[v_Governance_Template_Text]&p=1&nrOfHits=1000",
    "assessment_text": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%201000%20*%20FROM%20[MissionOnAdaptation].[latest].[v_Assessment_Template_Text]&p=1&nrOfHits=1000",
    "assessment_factors": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%201000%20*%20FROM%20[MissionOnAdaptation].[latest].[v_Assessment_Template_Factors_Text]&p=1&nrOfHits=1000",
    "assessment_risks": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%201000%20*%20FROM%20[MissionOnAdaptation].[latest].[v_Assessment_Template_Climate_Risk_Assessments_Text]&p=1&nrOfHits=1000",
    "action_text": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%201000%20*%20FROM%20[MissionOnAdaptation].[latest].[v_Action_Template_Text]&p=1&nrOfHits=1000",
    "action_actions": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%201000%20*%20FROM%20[MissionOnAdaptation].[latest].[v_Action_Template_Actions_Text]&p=1&nrOfHits=1000",
    "action_hazards": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%201000%20*%20FROM%20[MissionOnAdaptation].[latest].[v_Action_Template_Climate_Hazards_Text]&p=1&nrOfHits=1000",
    "action_sectors": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%201000%20*%20FROM%20[MissionOnAdaptation].[latest].[v_Action_Template_Sectors_Text]&p=1&nrOfHits=1000",
    "action_benefits": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%201000%20*%20FROM%20[MissionOnAdaptation].[latest].[v_Action_Template_Co_Benefits_Text]&p=1&nrOfHits=1000",
    "planning_titles": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%201000%20*%20FROM%20%5BMissionOnAdaptation%5D.%5Blatest%5D.%5Bv_Planning_Template_Adaptation_Text%5D&p=1&nrOfHits=1000",
    "planning_goals": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%201000%20*%20FROM%20%5BMissionOnAdaptation%5D.%5Blatest%5D.%5Bv_Planning_Template_Adaptation_Goals_Text%5D&p=1&nrOfHits=1000",
    "planning_goals_hazard": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%201000%20*%20FROM%20%5BMissionOnAdaptation%5D.%5Blatest%5D.%5Bv_Planning_Template_Adaptation_Goals_Climate_Hazards_Text%5D&p=1&nrOfHits=1000",
    "planning_climate_action": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%201000%20*%20FROM%20%5BMissionOnAdaptation%5D.%5Blatest%5D.%5Bv_Planning_Template_Climate_Action_Plan_Text%5D&p=1&nrOfHits=1000",
    "planning_climate_action_sectors": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%201000%20*%20FROM%20%5BMissionOnAdaptation%5D.%5Blatest%5D.%5Bv_Planning_Template_Climate_Action_Plan_Sectors_Text%5D&p=1&nrOfHits=1000",
    "tabs_labels": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%201000%20*%20FROM%20[MissionOnAdaptation].[latest].[v_Tabs_Text]&p=1&nrOfHits=1000",
    "footer_text": "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%20100%20*%20FROM%20%5BMissionOnAdaptation%5D.%5Blatest%5D.%5Bv_Footer_Text%5D&p=1&nrOfHits=50",
}


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


def parse_csv(path):
    try:
        wf = resource_filename("eea.climateadapt", path)
        with open(wf, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            # print(f"Headers: {reader.fieldnames}")
            return [row for row in reader]
    except Exception as e:
        logger.error(f"Failed to parse CSV {path}: {e}")
        return []


def get_assessment_sectors():
    raw_data = parse_csv("data/Assessment_Template_Grouped_Sectors_Text.csv")
    grouped = {}

    for row in raw_data:
        category_id = row["CategoryId"]
        category_name = row["Category_Name"]
        sector_name = row["Sector_Name"]
        order = int(row.get("Order", 999))

        key = (category_id, category_name, order)
        grouped.setdefault(key, []).append(sector_name)

    sorted_categories = sorted(grouped.items(), key=lambda x: x[0][2])

    return [
        {
            "CategoryId": key[0],
            "Category_Name": key[1],
            "Order": key[2],
            "Sectors": value,
        }
        for key, value in sorted_categories
    ]


def get_planning_data(profile_id):
    planning_goals = filter_by_profile_id(
        fetch_discodata_json(DISCODATA_URLS["planning_goals"]), profile_id
    )
    hazards_map = build_map(
        fetch_discodata_json(DISCODATA_URLS["planning_goals_hazard"]),
        ["Id", "Adaptation_Goal_Id"],
        "Climate_Hazard",
    )

    planning_climate_action = filter_by_profile_id(
        fetch_discodata_json(DISCODATA_URLS["planning_climate_action"]), profile_id
    )
    sectors_map = build_map(
        fetch_discodata_json(DISCODATA_URLS["planning_climate_action_sectors"]),
        ["Id", "Climate_Action_Plan_Id"],
        "Sector",
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
                fetch_discodata_json(DISCODATA_URLS["planning_titles"]), profile_id
            ),
            "planning_goals": planning_goals,
            "planning_climate_action": planning_climate_action,
        }
    }


def get_assessment_data(profile_id):
    return {
        "assessment": {
            "assessment_text": filter_by_profile_id(
                fetch_discodata_json(DISCODATA_URLS["assessment_text"]), profile_id
            ),
            "assessment_factors": filter_by_profile_id(
                fetch_discodata_json(DISCODATA_URLS["assessment_factors"]), profile_id
            ),
            "assessment_risks": filter_by_profile_id(
                fetch_discodata_json(DISCODATA_URLS["assessment_risks"]), profile_id
            ),
            "assessment_sectors": get_assessment_sectors(),
        }
    }


def get_action_data(profile_id):
    actions = filter_by_profile_id(
        fetch_discodata_json(DISCODATA_URLS["action_actions"]), profile_id
    )
    hazards_map = build_map(
        fetch_discodata_json(DISCODATA_URLS["action_hazards"]),
        ["Id", "Action_Id"],
        "Climate_Hazard",
    )
    sectors_map = build_map(
        fetch_discodata_json(DISCODATA_URLS["action_sectors"]),
        ["Id", "Action_Id"],
        "Sector",
    )
    benefits_map = build_map(
        fetch_discodata_json(DISCODATA_URLS["action_benefits"]),
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
                fetch_discodata_json(DISCODATA_URLS["action_text"]), profile_id
            ),
            "actions": actions,
        }
    }


def get_governance_data(profile_id):
    data = fetch_discodata_json(DISCODATA_URLS["governance"])
    return {"governance": filter_by_profile_id(data, profile_id)}


def get_tab_labels_data(_):
    try:
        rows = fetch_discodata_json(DISCODATA_URLS["tabs_labels"])
        if rows:
            first_row = rows[0]

            # Preserve order as defined by SQL column order
            tab_labels = [{"key": key, "value": first_row[key]} for key in first_row]

            return {"tab_labels": tab_labels}
        return {}
    except Exception as e:
        logger.error(f"Failed to process tab labels: {e}")
        return {}


def get_footer_text_data(_):
    data = fetch_discodata_json(DISCODATA_URLS["footer_text"])
    return {"footer_text": data[0]} if data else {}


def get_data_for_mission_signatory(profile_id):
    """Fetches data from the DISCODATA."""
    data_sections = [
        get_governance_data,
        get_planning_data,
        get_assessment_data,
        get_action_data,
        get_tab_labels_data,
        get_footer_text_data,
    ]
    result = {}

    for section in data_sections:
        try:
            result.update(section(profile_id))
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
        data = get_data_for_mission_signatory(profile_id)

        result = {
            "missionsignatoryprofile": {
                "@id": "{}/@missionsignatoryprofile".format(
                    self.context.absolute_url()
                ),
                "result": data,
            }
        }

        return result
