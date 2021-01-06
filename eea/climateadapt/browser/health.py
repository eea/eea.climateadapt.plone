import datetime
from collections import defaultdict
from zope.component.hooks import getSite

import DateTime
import plone.api as api
from Products.Five.browser import BrowserView


class HealthHomepageItems(BrowserView):

    def days_elapsed_mapping(self, p):
        mapping = [(80, 'big'), (90, 'med')]
        for check, value in mapping:
            if p <= check:
                return value
        return 'sma'

    def upcomingEvents(self):
        results = []

        now = DateTime.DateTime() - 1
        date_range_query = {'query': (now,), 'range': 'min'}

        portal_catalog = api.portal.get_tool('portal_catalog')
        items = portal_catalog.queryCatalog({
            "portal_type": "Event",
            "start": date_range_query,
            "sort_limit": "2",
            "review_state": "published",
            "sort_on": 'start',
            "Subject": ("Health Observatory", ),
        })

        for item in items:
            # TODO: don't convert DateTime to datetime and back
            days = (datetime.datetime.strptime(
                item.getObject().start.strftime('%d.%m.%Y'), '%d.%m.%Y')
                - datetime.datetime.now()
            ).days

            size = self.days_elapsed_mapping(days)
            info = {
                'title': item.Title,
                'size': size,
                'url': item.getURL(),
                'date': item.getObject().start.strftime('%d.%m.%Y'),
                "Subject": ("Health Observatory", ),
            }
            results.append(info)

        return results

    def latestNews(self):
        results = []
        portal_catalog = api.portal.get_tool('portal_catalog')
        items = portal_catalog.queryCatalog({
            "portal_type": "News Item",
            "sort_limit": "2",
            "review_state": "published",
            "sort_on": 'created',
            "sort_order": 'descending',
            "Subject": ("Health Observatory", ),
        })

        strptime = datetime.datetime.strptime

        for item in items:
            # TODO: don't convert DateTime to datetime and back
            created = item.getObject().created().strftime('%d.%m.%Y')
            now = datetime.datetime.now()
            days = (strptime(created, '%d.%m.%Y') - now).days

            size = self.days_elapsed_mapping(days * -1)
            info = {
                'title': item.Title,
                'size': size,
                'url': item.getURL(),
                'date': item.getObject().created().strftime('%d.%m.%Y')
            }
            results.append(info)

        return results

    @property
    def more_news(self):
        site = getSite()
        url = site['news-archive'].absolute_url()
        return [url, "More news"]

    @property
    def more_events(self):
        site = getSite()
        url = site['more-events'].absolute_url()
        return [url, "More events"]
