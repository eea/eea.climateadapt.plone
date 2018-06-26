from functools import partial
from collections import defaultdict
from collections import namedtuple

from Products.Five.browser import BrowserView
from plone.app.layout.viewlets.content import ContentHistoryViewlet

import plone.api as api


FMT_DATE = '%d-%m-%Y'

TYPES = (
    'eea.climateadapt.indicator',
    'eea.climateadapt.publicationreport',
    'eea.climateadapt.informationportal',
    'eea.climateadapt.guidancedocument',
    'eea.climateadapt.tool',
    'eea.climateadapt.aceproject',
    'eea.climateadapt.adaptationoption',
    'eea.climateadapt.casestudy',
    'eea.climateadapt.organisation',
    'eea.climateadapt.mapgraphdataset',
)


PATHS = (
    'metadata/indicators',
    'metadata/publications',
    'metadata/portals',
    'metadata/guidances',
    'metadata/tools',
    'metadata/projects',
    'metadata/adaptation-options',
    'metadata/case-studies',
    'metadata/organisations',
    'metadata/map-graphs',
)


NAMES = (
    'Indicator',
    'Publication and Report',
    'Information Portal',
    'Guidance Document',
    'Tool',
    'Research and Knowledge Project',
    'Adaptation Option',
    'Case Study',
    'Organization',
    'Map, Graph or Dataset',
)


TYPE_INFO = zip(TYPES, PATHS, NAMES)

Entry = namedtuple('Entry', (
    'brain',
    'portal_type',
    'url',
    'title',
    'user_name',
    'user_id',
    'created',
    'modified',
    'history',
))


def extract_metadata(brain):
    created = brain.created.strftime(FMT_DATE)
    modified = brain.modified.strftime(FMT_DATE)

    user_id = brain.Creator
    member = api.user.get(user_id)
    user_name = member.getProperty('fullname') if member else user_id

    obj = brain.getObject()
    # history_view = ContentHistoryViewlet(obj, obj.REQUEST, 'historyview')
    # history_view.update()
    # history = history_view.fullHistory()
    # history = history_view.revisionHistory()
    history = []
    # import pdb; pdb.set_trace()

    return Entry(
        brain, brain.portal_type, brain.getURL(), brain.Title,
        user_name, user_id, created, modified, history,
    )


def classify_brains(acc, brain):
    acc[brain.portal_type].append(extract_metadata(brain))
    return acc


class DashboardView(BrowserView):
    def items(self):
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(portal_type=TYPES)

        classified = reduce(classify_brains, brains, defaultdict(list))

        for portal_type, path, name in TYPE_INFO:
            yield dict(
                portal_type=portal_type,
                path=path,
                name=name,
                entries=classified[portal_type],
            )
