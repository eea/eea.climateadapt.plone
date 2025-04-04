import json

from lxml.etree import Element, SubElement, tostring
from zope.interface import classImplements

from eea.climateadapt.browser import AceViewApi
from eea.climateadapt.vocabulary import _relevance
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.browser.view import DefaultView
from plone.dexterity.interfaces import IDexterityEditForm
from plone.memoize import view
from plone.transformchain.interfaces import DISABLE_TRANSFORM_REQUEST_KEY
from plone.z3cform import layout
from plone.z3cform.fieldsets.extensible import FormExtender
from Products.CMFPlone.utils import getToolByName
from Products.Five.browser import BrowserView


class CaseStudyView(DefaultView, AceViewApi):
    """ Default view for case studies
    """

    @view.memoize
    def get_adaptation_options(self):
        # TODO: filter by published

        return [o.to_object for o in self.context.adaptationoptions]

    @view.memoize
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
        # import pdb; pdb.set_trace()
        self.move('IGeolocatable.geolocation', after='geochars')
        self.move('description', before='long_description')
        self.move('primary_photo', after='long_description')
        self.move('primary_photo_copyright', after='primary_photo')
        self.move('relevance', after='climate_impacts')
        self.move('solutions', after='climate_impacts')
        self.move('adaptationoptions', after='climate_impacts')
        self.move('objectives', after='climate_impacts')
        self.move('challenges', after='climate_impacts')
        self.move('contact', before='websites')
        self.remove('ICategorization.subjects')
        self.remove('ICategorization.language')
        self.remove('IPublication.effective')
        self.remove('IPublication.expires')
        self.remove('IOwnership.creators')
        self.remove('IOwnership.contributors')
        self.remove('IOwnership.rights')
        labels = ['label_schema_dates',
                  'label_schema_ownership', 'Layout', 'Settings']
        self.form.groups = [
            group for group in self.form.groups if len(
                list(group.fields.values())) > 0 and group.label not in labels
        ]


class CaseStudyJson(BrowserView):
    """ @@json view
    """

    def __call__(self):
        return json.dumps(self.context._repr_for_arcgis())


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

        for brain in cat.searchResults(
            portal_type='eea.climateadapt.casestudy',
            review_state='published'
        ):
            cs = brain.getObject()
            res.append(cs._repr_for_arcgis())

        return json.dumps(res)


class CaseStudiesXML(BrowserView):
    """ A view to return all case studies as XML.

    Useful in debugging in developing the SAT mapping tool. See CaseStudiesJson

    for details on meaning of data.
    """

    def __call__(self):
        self.request.environ[DISABLE_TRANSFORM_REQUEST_KEY] = True

        cat = getToolByName(self.context, 'portal_catalog')
        root = Element("casestudies")

        for brain in cat.searchResults(
            portal_type='eea.climateadapt.casestudy',
            review_state='published'
        ):
            cs = brain.getObject()
            cs = cs._repr_for_arcgis()
            e_cs = SubElement(root, 'casestudy')
            e_attrs = SubElement(e_cs, 'attributes')

            for k, v in list(cs['attributes'].items()):
                el = Element(k)

                if isinstance(v, str):
                    el.text = v.decode('utf-8').strip()
                else:
                    el.text = str(v).strip()
                e_attrs.append(el)
            e_geo = SubElement(e_cs, 'geometry')

            for k, v in list(cs['geometry'].items()):
                el = Element(k)
                el.text = str(v)
                e_geo.append(el)

        res = tostring(root, pretty_print=True)

        return res
