import csv
import json
import urllib2
import logging
from pkg_resources import resource_filename


logger = logging.getLogger("eea.climateadapt")

DISCODATA_URL = "https://discodata.eea.europa.eu/sql?query=select%20*%20from%20%5BNCCAPS%5D.%5Blatest%5D.%5BAdaptation_Art19_JSON_2023%5D&p=1&nrOfHits=1"
CSV_FILE_PATH = "governance.csv" 


def parse_csv(path):
    wf = resource_filename("eea.climateadapt.mission_signatories", path)

    reader = csv.reader(open(wf))
    cols = reader.next()
    out = []
    out = [dict(zip(cols, line)) for line in reader]
    return out

def get_discodata_for_mission_signatories(id=None):
    """Fetches data from the DISCODATA. """
    try:
        # response = urllib2.urlopen(DISCODATA_URL)
        # data = json.loads(response.read())
        # return data['results']

        # test with real data from csv file
        results = parse_csv(CSV_FILE_PATH)
        if id is not None:
            results = [item for item in results if item['Id'] == str(id)]

        return results

    except urllib2.URLError as e:
        logger.error("Failed to fetch data: %s", e)
        return None
    except ValueError as e:
        logger.error("Failed to parse JSON: %s", e)
        return None