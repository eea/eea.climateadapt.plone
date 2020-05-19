# from functools import partial
from collections import defaultdict, namedtuple

import DateTime
import datetime
import plone.api as api
from Products.Five.browser import BrowserView


class HealthHomepageItems(BrowserView):

    def getFolderContext(self):
        return self.context.description

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

            if days<10:
                size='big'
            elif days<21:
                size='med'
            else:
                size='sma'
            object = {
                'title': item.getObject().title,
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

            if days>-7:
                size='big'
            elif days>-14:
                size='med'
            else:
                size='sma'
            object = {
                'title': item.getObject().title,
                'size': size,
                'url': item.getURL(),
                'date': item.getObject().created().strftime('%d.%m.%Y')
                }
            results.append(object)

        return results

    def trendsProjections(self):
        response = 0

        portal_catalog = api.portal.get_tool('portal_catalog')
        items = portal_catalog.queryCatalog(
                {"portal_type":"health_home_trends_projection",
                "sort_limit":"5",
                "review_state":"published"}
                )
        for item in items:
            response = {
                'title': item.getObject().title,
                'right_description': item.getObject().rightdescription.output,
                'bottom_description': item.getObject().bottom_description.output,
                'source_website': item.getObject().source_website,
                'tags': item.getObject().subject
            }
        return response

    def heatExtrems(self):
        results = []

        portal_catalog = api.portal.get_tool('portal_catalog')
        items = portal_catalog.queryCatalog(
                {"portal_type":"health_heat_extremes",
                "sort_limit":"5",
                "review_state":"published"}
                )
        for item in items:
            results.append({
                'title': item.getObject().title,
                'description': item.getObject().long_description,
                'url': item.getObject().url_more,
                'item_url': item.getURL(),
            })
        return results
