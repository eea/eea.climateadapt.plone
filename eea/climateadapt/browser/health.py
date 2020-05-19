# from functools import partial
from collections import defaultdict, namedtuple

import DateTime
import datetime
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
        date_range_query = { 'query':(now,), 'range': 'min'}

        portal_catalog = api.portal.get_tool('portal_catalog')
        items = portal_catalog.queryCatalog({
                "portal_type":"Event",
                "start" : date_range_query,
                "sort_limit":"5",
                "review_state":"published",
                "sort_on":'start'
            })

        for item in items:
            days = (datetime.datetime.strptime(
                        item.getObject().start.strftime('%d.%m.%Y'),'%d.%m.%Y')
                        -datetime.datetime.now()
                    ).days

            size = self.days_elapsed_mapping(days)
            object = {
                'title': item.Title,
                'size': size,
                'url': item.getURL(),
                'date': item.getObject().start.strftime('%d.%m.%Y')
                }
            results.append(object)

        return results

    def latestNews(self):
        results = []
        portal_catalog = api.portal.get_tool('portal_catalog')
        items = portal_catalog.queryCatalog({
                "portal_type":"News Item",
                "sort_limit":"5",
                "review_state":"published",
                "sort_on":'created',
                "sort_order":'descending'
            })

        for item in items:
            days = (datetime.datetime.strptime(
                    item.getObject().created().strftime('%d.%m.%Y'),'%d.%m.%Y')
                    -datetime.datetime.now()
                ).days

            size = self.days_elapsed_mapping(days*-1)
            object = {
                'title': item.Title,
                'size': size,
                'url': item.getURL(),
                'date': item.getObject().created().strftime('%d.%m.%Y')
                }
            results.append(object)

        return results
