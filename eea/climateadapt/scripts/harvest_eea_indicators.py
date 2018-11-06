
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dateutil.parser import parse

from eea.climateadapt.scripts import get_plone_site
from sparql import query  # SparqlException,

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

BOOTSTRAP = '<link rel="stylesheet" type="text/css" ' \
            'href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.1/css/bootstrap.min.css">'
STYLE = '<style> th, td {padding: 5px;}</style>'

SUBJECT = "New indicators were harvested from SDS"
MESSAGE_TITLE = "<h4>The following indicators were recently created or modified, " \
                "please create/update their content</h4>"

from_ = "laszlo.cseh@eaudeweb.ro"
to_ = ("laszlo.cseh@eaudeweb.ro",)
error_to = ("laszlo.cseh@eaudeweb.ro",)


def create_message(result):
    hasresult = False

    message = list()
    message.append(BOOTSTRAP)
    message.append(STYLE)
    message.append('<table class="table-bordered">')

    variables = result.variables
    message.append("<tr>")

    for variable in variables:
        message.append("<th>{}</th>".format(variable))
    message.append("</tr>")

    for row in result.fetchone():
        hasresult = True
        message.append("<tr>")

        for i in range(0, len(variables)):
            value = unicode(row[i])

            if row[i].__class__.__name__ == 'IRI':
                html_value = "<td><a href={0}>{0}</a></td>".format(value)
            elif getattr(row[i], 'datatype', '') == 'http://www.w3.org/2001/XMLSchema#dateTime':
                date = parse(value).strftime('%d %b %Y, %H:%M:%S')
                html_value = "<td>{0}</td>".format(date)
            else:
                html_value = "<td>{0}</td>".format(value)

            message.append(html_value)

        message.append("</tr>")

    message.append("</table>")

    return "".join(message), hasresult


def send_email(msg):
    msg['From'] = from_
    site = get_plone_site()
    site.MailHost.send(
        messageText=msg,
        immediate=True
    )


def main():
    msg = MIMEMultipart('alternative')

    try:
        result = query(ENDPOINT, Q)

        message, hasresult = create_message(result)
        message_text = "".join((MESSAGE_TITLE, message))

        html_part = MIMEText(message_text, 'html')
        msg.attach(html_part)

        if hasresult:
            msg['To'] = ",".join(to_)
            msg['Subject'] = SUBJECT

            send_email(msg)

    except Exception as e:
        error_text = "; ".join((repr(e), e.code))
        text_part = MIMEText(error_text, 'html')
        msg['To'] = ",".join(error_to)
        msg['Subject'] = '[ERROR] ' + SUBJECT
        msg.attach(text_part)

        send_email(msg)


if __name__ == "__main__":
    main()
