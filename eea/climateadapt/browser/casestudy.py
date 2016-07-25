from Products.CMFPlone.utils import getToolByName
from Products.Five.browser import BrowserView
from eea.climateadapt.browser import AceViewApi
from eea.climateadapt.vocabulary import _relevance
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.browser.view import DefaultView
from plone.dexterity.interfaces import IDexterityEditForm
from plone.z3cform import layout
from plone.z3cform.fieldsets.extensible import FormExtender
from zope.interface import classImplements
import json
import time


class CaseStudyView(DefaultView, AceViewApi):
    """ Default view for case studies
    """

    def get_adaptation_options(self):
        # TODO: filter by published
        return [o.to_object for o in self.context.adaptationoptions]

    def relevances_dict(self):
        return dict(_relevance)


class CaseStudyEditForm(DefaultEditForm):
    """ Edit form for case studies
    """

CaseStudyEditView = layout.wrap_form(CaseStudyEditForm)
classImplements(CaseStudyEditView, IDexterityEditForm)


class CaseStudyAddForm(DefaultAddForm):
    """ Add Form for case studies
    """


class CaseStudyFormExtender(FormExtender):
    def update(self):
        self.move('IGeolocatable.geolocation', after='geochars')
        self.move('primary_photo', after='long_description')
        self.move('relevance', after='climate_impacts')
        self.move('solutions', after='climate_impacts')
        self.move('adaptationoptions', after='climate_impacts')
        self.move('objectives', after='climate_impacts')
        self.move('challenges', after='climate_impacts')
        self.move('contact', before='websites')


def _unixtime(d):
    try:
        return int(time.mktime(d.utctimetuple()))
    except AttributeError:
        return ""


def cs_to_json(cs):
    return {
        'attributes': {
            'area':     '',
            'itemname': cs.Title(),
            'desc_':    cs.long_description
            and cs.long_description.output or '',   # todo: strip
            'website':  ';'.join(cs.websites or []),
            'sectors':  ';'.join(cs.sectors or []),
            'risks':    ';'.join(cs.climate_impacts or []),
            'measureid': brain.getURL(),
            'featured': 'no',
            'newitem': 'no',
            'casestudyf': '',
            'client_cls': '',
            'CreationDate': _unixtime(cs.creation_date),
            'Creator': cs.creators[-1],
            'EditDate': _unixtime(cs.modification_date),
            'Editor': cs.workflow_history[
                'cca_items_workflow'][-1]['actor'],
        },
        'geometry': {'x': geo and geo.latitude or '',
                     'y': geo and geo.longitude or ''}
    }


class CaseStudyJson(BrowserView):
    """ @@json view
    """
    def __call__(self):
        return json.dumps(cs_to_json(self.context))


class CaseStudiesJson(BrowserView):
    """ A view to return all case studies as JSON.

    Useful in debugging in developing the SAT mapping tool

    Fields:
        [u'FID',            # internal id field in GIS?
        u'area',            # biogeographical region from geochar
        u'itemname',        # title
        u'desc_',           # u'desc_': u'<p>The Hedwige-Prosper Polder project is part of the <span></p></span>',
        u'website',         # 'www.stadtklima-stuttgart.de/index.php?climate_climate_atlas_2008;www.stadtklima-stuttgart.de/index.php?start_e;www.grabs-eu.org/membersArea/files/stuttgart.pdf'
        u'sectors',         # 'BIODIVERSITY;COASTAL;WATERMANAGEMENT;',
        u'risks',           # u'FLOODING;SEALEVELRISE;',
        u'measureid',       # a number
        u'featured',        # "yes" or "no",
        u'newitem',         # "yes" or "no"
        u'casestudyf',      # u'casestudyf': u'CASEHOME;CASESEARCH;',
        u'client_cls',      # "featured" or "featured-highlight" or "normal" or "highlight"
        u'CreationDate',    # Unix timestamp
        u'Creator',         # user id
        u'EditDate',        # Unix timestamp
        u'Editor'           # user id
        ]
    Geometry such as: u'geometry': {u'x': -413371.4, u'y': 4927436.6}
    """

    def __call__(self):
        cat = getToolByName(self.context, 'portal_catalog')
        res = []
        for brain in cat.searchResults(portal_type='eea.climateadapt.casestudy'):
            cs = brain.getObject()
            geo = cs.geolocation
            res.append(cs_to_json(cs))
        return json.dumps(res)
