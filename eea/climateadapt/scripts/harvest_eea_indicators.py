
from dateutil.parser import parse
from sparql import SparqlException, query
from eea.climateadapt.scripts import get_plone_site

from zope.event import notify
from eea.climateadapt.indicator import (IndicatorMessageEvent,
    threadlocals, MESSAGE_KEY)

DAYS = 1
ENDPOINT = "http://semantic.eea.europa.eu/sparql"
Q = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX cr: <http://cr.eionet.europa.eu/ontologies/contreg.rdf#>

SELECT  ?resource, ?modified, ?created 
WHERE {

?resource a <http://www.eea.europa.eu/portal_types/Specification#Specification>;
   <http://purl.org/dc/terms/created> ?created;
   <http://purl.org/dc/terms/modified> ?modified

bind(NOW() as ?today)
bind(xsd:date(concat(str(year(?today)),"-", str(month(?today)),"-", str(day(?today)))) 
   as ?date_today)
bind(xsd:date(concat(str(year(?created)),"-", str(month(?created)),"-", str(day(?created)))) 
   as ?date_created)
bind(?date_today - ?modified as ?difference)
FILTER(?difference <= 86400*%s)

} ORDER BY desc(?modified)  
        """ % DAYS


def create_message(result):
    message = list()
    variables = result.variables

    for row in result.fetchone():
        m = list()
        for i in range(0, len(variables)):
            value = str(row[i])

            if row[i].__class__.__name__ == 'IRI':
                # formatted_value = "<a href={0}>{0}</a>".format(value)
                formatted_value = value
            elif getattr(row[i], 'datatype', '') == 'http://www.w3.org/2001/XMLSchema#dateTime':
                formatted_value = parse(value).strftime('%d %b %Y, %H:%M:%S')
            else:
                formatted_value = value

            m.append("{}: {}".format(variables[i], formatted_value))

        message.append("\n".join(m))

    return "\n------------\n".join(message)


def trigger_content_rule(message):
    setattr(threadlocals, MESSAGE_KEY, message)
    site = get_plone_site()
    notify(IndicatorMessageEvent(site))


def main():
    try:
        result = query(ENDPOINT, Q)

        message = create_message(result)

        if message:
            trigger_content_rule(message)

    except Exception as e:
        error_text = "; ".join((repr(e), e.code))
        trigger_content_rule(error_text)


if __name__ == "__main__":
    main()
