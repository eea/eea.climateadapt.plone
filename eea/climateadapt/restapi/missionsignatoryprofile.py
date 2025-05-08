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

GOVERNANCE_DISCODATA_URL = "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%201000%20*%20FROM%20%5BMissionOnAdaptation%5D.%5Blatest%5D.%5Bv_Governance_Template_Text%5D&p=1&nrOfHits=1000"


def fetch_discodata_json(url):
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        logger.error(f"Failed to fetch or parse JSON from {url}: {e}")
        return {"results": []}


def filter_discodata_by_profile_id(data, profile_id):
    """Filter results by profile ID."""
    if not profile_id:
        return data
    return [row for row in data if str(row.get("Id")) == str(profile_id)]


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


def filter_rows_by_id(rows, profile_id):
    return [row for row in rows if row.get("Id") == str(profile_id)]


def get_planning_data(profile_id):
    planning_goals_csv = parse_csv("./data/Planning_Template_Adaptation_Goals_Text.csv")
    planning_titles_csv = parse_csv("./data/Planning_Template_Adaptation_Text.csv")
    climate_hazards_csv = parse_csv(
        "./data/Planning_Template_Adaptation_Goals_Climate_Hazards_Text.csv"
    )
    climate_actions_csv = parse_csv(
        "./data/Planning_Template_Climate_Action_Plan_Text.csv"
    )
    climate_sectors_csv = parse_csv(
        "./data/Planning_Template_Climate_Action_Plan_Sectors_Text.csv"
    )

    hazard_map = {}
    for hazard in climate_hazards_csv:
        key = (hazard.get("Id"), hazard.get("Adaptation_Goal_Id"))
        hazard_map.setdefault(key, []).append(hazard.get("Climate_Hazard"))

    sector_map = {}
    for sector in climate_sectors_csv:
        key = (sector.get("Id"), sector.get("Climate_Action_Plan_Id"))
        sector_map.setdefault(key, []).append(sector.get("Sector"))

    # Filter planning goals and attach hazards
    planning_goals = []
    for row in filter_rows_by_id(planning_goals_csv, profile_id):
        key = (row.get("Id"), row.get("Adaptation_Goal_Id"))
        row["Climate_Hazards"] = hazard_map.get(key, [])
        planning_goals.append(row)

    # Filter and attach sectors to climate actions
    climate_actions = []
    for row in filter_rows_by_id(climate_actions_csv, profile_id):
        key = (row.get("Id"), row.get("Climate_Action_Plan_Id"))
        row["Sectors"] = sector_map.get(key, [])
        climate_actions.append(row)

    planning_titles = filter_rows_by_id(planning_titles_csv, profile_id)

    return {
        "planning": {
            "planning_goals": planning_goals,
            "planning_titles": planning_titles,
            "planning_climate_action": climate_actions,
        }
    }


def get_assessment_data(profile_id):
    assessment_text_csv = parse_csv("./data/Assessment_Template_Text.csv")
    assessment_factors_csv = parse_csv("./data/Assessment_Template_Factors_Text.csv")
    assessment_risks_csv = parse_csv(
        "./data/Assessment_Template_Climate_Risk_Assessments_Text.csv"
    )

    assessment_text = filter_rows_by_id(assessment_text_csv, profile_id)
    assessment_factors = filter_rows_by_id(assessment_factors_csv, profile_id)
    assessment_risks = filter_rows_by_id(assessment_risks_csv, profile_id)

    return {
        "assessment": {
            "assessment_text": assessment_text,
            "assessment_factors": assessment_factors,
            "assessment_risks": assessment_risks,
        }
    }


def get_action_data(profile_id):
    action_text_csv = parse_csv("./data/Action_Template_Text.csv")
    actions_csv = parse_csv("./data/Action_Template_Actions_Text.csv")
    actions_hazards_csv = parse_csv("./data/Action_Template_Climate_Hazards_Text.csv")
    actions_sectors_csv = parse_csv("./data/Action_Template_Sectors_Text.csv")
    actions_benefits_csv = parse_csv("./data/Action_Template_Co_Benefits_Text.csv")

    hazard_map = {}
    for hazard in actions_hazards_csv:
        key = (hazard.get("Id"), hazard.get("Action_Id"))
        hazard_map.setdefault(key, []).append(hazard.get("Climate_Hazard"))

    sectors_map = {}
    for sector in actions_sectors_csv:
        key = (sector.get("Id"), sector.get("Action_Id"))
        sectors_map.setdefault(key, []).append(sector.get("Sector"))

    benefits_map = {}
    for benefit in actions_benefits_csv:
        key = (benefit.get("Id"), benefit.get("Action_Id"))
        benefits_map.setdefault(key, []).append(benefit.get("Co_Benefit"))

    # Filter actions and attach hazards, sectors, and co-benefits
    actions = []
    for row in filter_rows_by_id(actions_csv, profile_id):
        key = (row.get("Id"), row.get("Action_Id"))
        row["Climate_Hazards"] = hazard_map.get(key, [])
        row["Sectors"] = sectors_map.get(key, [])
        row["Co_Benefits"] = benefits_map.get(key, [])
        actions.append(row)

    action_text = filter_rows_by_id(action_text_csv, profile_id)

    return {
        "action": {
            "action_text": action_text,
            "actions": actions,
        }
    }


def get_governance_data(profile_id):
    governance_json = fetch_discodata_json(GOVERNANCE_DISCODATA_URL)
    governance_data = governance_json.get("results", [])
    result = filter_discodata_by_profile_id(governance_data, profile_id)

    return {"governance": result}


def get_data_for_mission_signatory(id=None):
    """Fetches data from the DISCODATA."""
    try:
        data_sections = [
            get_governance_data,
            get_planning_data,
            get_assessment_data,
            get_action_data,
        ]

        result = {}
        for section in data_sections:
            result.update(section(id))

        return result

    except ValueError as e:
        logger.error("Failed to parse JSON: %s", e)
        return None


@implementer(IExpandableElement)
@adapter(IMissionSignatoryProfile, Interface)
class MissionSignatoryProfile(object):
    """An expander that inserts the data of a mission signatory profile"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        absolute_url = self.context.absolute_url()
        id = absolute_url.rstrip("/").split("/")[-1]
        data = get_data_for_mission_signatory(id)

        try:
            data = get_data_for_mission_signatory(id)
        except Exception as e:
            logger.warning(
                "Error in processing mission signatory profile: {}".format(e)
            )

        result = {
            "missionsignatoryprofile": {
                "@id": "{}/@missionsignatoryprofile".format(
                    self.context.absolute_url()
                ),
                "result": data,
            }
        }

        return result
