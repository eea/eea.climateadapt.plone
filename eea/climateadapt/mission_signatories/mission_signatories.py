import csv

# import json
# import urllib2
import logging
from pkg_resources import resource_filename


logger = logging.getLogger("eea.climateadapt")

DISCODATA_URL = "https://discodata.eea.europa.eu/sql?query=select%20*%20from%20%5BNCCAPS%5D.%5Blatest%5D.%5BAdaptation_Art19_JSON_2023%5D&p=1&nrOfHits=1"


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
        key = (hazard.get("Id"), hazard.get("Adaptation_GoalId"))
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
        # response = urllib2.urlopen(DISCODATA_URL)
        # data = json.loads(response.read())
        # return data['results']

        result = {}

        # Governance section
        governance_data = parse_csv("governance.csv")
        result["governance"] = (
            filter_rows_by_id(governance_data, id) if id else governance_data
        )

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
