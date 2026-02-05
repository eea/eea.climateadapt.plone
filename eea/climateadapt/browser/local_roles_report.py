import csv
import io
from Products.Five.browser import BrowserView
from plone import api
from eea.climateadapt.local_roles import get_local_roles_report


class LocalRolesReportView(BrowserView):
    """A view to report local roles across the portal."""

    def __call__(self):
        include_owner = self.request.form.get("full", "0")
        if include_owner in ("0", "false", "False", ""):
            include_owner = False
        else:
            include_owner = True

        output_format = self.request.form.get("format", "html")

        portal = api.portal.get()
        data = get_local_roles_report(portal, include_owner=include_owner)

        if output_format == "csv":
            return self.render_csv(data)

        return self.render_html(data, include_owner)

    def render_csv(self, data):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Path", "Principal", "Roles", "Inheritance Blocked"])

        for entry in data:
            path = entry["path"]
            blocked = entry["blocked"]
            if not entry["roles"]:
                writer.writerow([path, "(no local roles)", "", blocked])
            for principal, role_list in entry["roles"]:
                writer.writerow([path, principal, ", ".join(role_list), blocked])

        self.request.response.setHeader("Content-Type", "text/csv")
        self.request.response.setHeader(
            "Content-Disposition", 'attachment; filename="local_roles_report.csv"'
        )
        return output.getvalue()

    def render_html(self, data, include_owner):
        html = []
        html.append("<html><body>")
        html.append("<h1>Local Roles Report</h1>")
        html.append(f"<p>Full report (including Owners): {include_owner}</p>")
        html.append('<p><a href="?format=csv' + ("&full=1" if include_owner else "") + '">Download CSV</a> | ')
        if include_owner:
            html.append('<a href="?full=0">Hide Owners</a></p>')
        else:
            html.append('<a href="?full=1">Show Owners</a></p>')

        for entry in data:
            html.append(f"<h3>{entry['path']}</h3>")
            if entry["blocked"]:
                html.append("<p style='color: red; font-weight: bold;'>[Inheritance BLOCKED]</p>")

            if not entry["roles"]:
                html.append("<ul><li>(no local roles)</li></ul>")
                continue

            html.append("<ul>")
            for principal, role_list in entry["roles"]:
                html.append(f"<li><b>{principal}</b>: {', '.join(role_list)}</li>")
            html.append("</ul>")

        html.append("</body></html>")
        return "\n".join(html)
