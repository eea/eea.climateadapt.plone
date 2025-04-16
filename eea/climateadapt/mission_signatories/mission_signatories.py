import csv

import json
import urllib.request
import logging
from pkg_resources import resource_filename


logger = logging.getLogger("eea.climateadapt")

GOVERNANCE_DISCODATA_URL = "https://discodata.eea.europa.eu/sql?query=SELECT%20TOP%20100%20*%20FROM%20%5BMissionOnAdaptation%5D.%5Blatest%5D.%5Bv_Governance_Template_Text%5D&p=1&nrOfHits=100"


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
        wf = resource_filename("eea.climateadapt.mission_signatories", path)
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
    planning_goals_csv = parse_csv("Planning_Template_Adaptation_Goals_Text.csv")
    planning_titles_csv = parse_csv("Planning_Template_Adaptation_Text.csv")
    climate_hazards_csv = parse_csv(
        "Planning_Template_Adaptation_Goals_Climate_Hazards_Text.csv"
    )
    climate_actions_csv = parse_csv("Planning_Template_Climate_Action_Plan_Text.csv")
    climate_sectors_csv = parse_csv(
        "Planning_Template_Climate_Action_Plan_Sectors_Text.csv"
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
        "planning_goals": planning_goals,
        "planning_titles": planning_titles,
        "planning_climate_action": climate_actions,
    }


def get_discodata_for_mission_signatories(id=None):
    """Fetches data from the DISCODATA."""
    try:
        result = {}

        # governance_data = parse_csv("Governance.csv")
        # result["governance"] = (
        #     filter_rows_by_id(governance_data, id) if id else governance_data
        # )

        # Governance section
        governance_json = fetch_discodata_json(GOVERNANCE_DISCODATA_URL)
        governance_data = governance_json.get("results", [])
        result["governance"] = filter_discodata_by_profile_id(governance_data, id)

        # Planning section
        planning_data = get_planning_data(id)
        result.update(planning_data)

        return result

    # except urllib2.URLError as e:
    #     logger.error("Failed to fetch data: %s", e)
    #     return None
    except ValueError as e:
        logger.error("Failed to parse JSON: %s", e)
        return None
