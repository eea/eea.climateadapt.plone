# from functools import partial
from collections import defaultdict, namedtuple

import plone.api as api
from Products.Five.browser import BrowserView
from functools import reduce

# from plone.app.layout.viewlets.content import ContentHistoryViewlet


FMT_DATE = '%d-%m-%Y'


TYPE_INFO = [
    ('eea.climateadapt.indicator',
     'metadata/indicators',
     'Indicator'
     ),
    ('eea.climateadapt.publicationreport',
     'metadata/publications',
     'Publication and Report',
     ),
    ('eea.climateadapt.informationportal',
     'metadata/portals',
     'Information Portal',),
    ('eea.climateadapt.guidancedocument',
     'metadata/guidances',
     'Guidance Document'
     ),
    ('eea.climateadapt.tool',
     'metadata/tools',
     'Tool',),
    ('eea.climateadapt.aceproject',
     'metadata/projects',
     'Research and Knowledge Project'),
    ('eea.climateadapt.adaptationoption',
     'metadata/adaptation-options',
     'Adaptation Option'),
    ('eea.climateadapt.casestudy',
     'metadata/case-studies',
     'Case Study'),
    ('eea.climateadapt.organisation',
     'metadata/organisations',
     'Organization'),
    ('eea.climateadapt.mapgraphdataset',
     'metadata/map-graphs',
     'Map, Graph or Dataset'),
]

TYPES = [x[0] for x in TYPE_INFO]

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
    'review_state',
))


def extract_metadata(brain):
    created = brain.created.strftime(FMT_DATE)
    modified = brain.modified.strftime(FMT_DATE)

    user_id = brain.Creator
    member = api.user.get(user_id)
    user_name = member.getProperty('fullname') if member else user_id

    # obj = brain.getObject()
    # history_view = ContentHistoryViewlet(obj, obj.REQUEST, 'historyview')
    # history_view.update()
    # history = history_view.fullHistory()
    # history = history_view.revisionHistory()
    history = []

    return Entry(
        brain,
        brain.portal_type,
        brain.getURL(),
        brain.Title,
        user_name,
        user_id,
        created,
        modified,
        history,
        brain.review_state,
    )


def classify_brains(acc, brain):
    acc[brain.portal_type].append(extract_metadata(brain))

    return acc


class DashboardView(BrowserView):
    def plural(self, name):
        if name[-1] == 'y':
            name = name[:-1] + 'ies'
        else:
            name = name + 's'

        return name

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
