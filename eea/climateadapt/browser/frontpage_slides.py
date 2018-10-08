import json
import urllib
from collections import namedtuple

from zope.interface import implements
from zope.lifecycleevent import modified
from zope.schema import TextLine

from eea.climateadapt.interfaces import IEEAClimateAdaptInstalled
from plone import api
from plone.api.portal import get_tool
from plone.app.textfield import RichText
from plone.directives import dexterity, form
from plone.namedfile.field import NamedBlobImage
from plone.namedfile.interfaces import IImageScaleTraversable
from Products.Five.browser import BrowserView


class RichImageSchema(form.Schema, IImageScaleTraversable):
    form.fieldset('default',
                  label=u'Item Description',
                  fields=['title', 'long_description', 'rich_image']
                  )

    title = TextLine(title=(u"Title"),
                     description=u"Item Name (250 character limit)",
                     required=True)

    long_description = RichText(title=(u"Description"),
                                description=u"Provide a description of the "
                                u"item.(5,000 character limit)",
                                required=True)

    rich_image = NamedBlobImage(
        title=(u"Image"),
        required=True,
    )


class IRichImage(RichImageSchema):
    """ Interface for the RichImage content type """


class RichImage(dexterity.Container):
    """ Image content type for which we the richtext behavior is activated """
    implements(IRichImage, IEEAClimateAdaptInstalled)

    def html2text(self, html):
        if not isinstance(html, basestring):
            return u""
        portal_transforms = api.portal.get_tool(name='portal_transforms')
        data = portal_transforms.convertTo('text/plain',
                                           html, mimetype='text/html')
        text = data.getData()

        return text.strip()

    def PUT(self, REQUEST=None, RESPONSE=None):
        """DAV method to replace image field with a new resource."""
        request = REQUEST if REQUEST is not None else self.REQUEST
        response = RESPONSE if RESPONSE is not None else request.response

        self.dav__init(request, response)
        self.dav__simpleifhandler(request, response, refresh=1)

        infile = request.get('BODYFILE', None)
        filename = request['PATH_INFO'].split('/')[-1]
        self.image = NamedBlobImage(
            data=infile.read(), filename=unicode(filename))

        modified(self)

        return response

    def get_size(self):
        return getattr(self.image, 'size', None)

    def content_type(self):
        return getattr(self.image, 'contentType', None)


Section = namedtuple('Section',
                     ['title', 'count', 'link', 'icon_class'])

SEARCH_TYPES_ICONS = [
    ("MEASURE", "Adaptation options", 'fa-cogs'),
    ("ACTION", "Case studies", 'fa-file-text-o'),
    ("GUIDANCE", "Guidance", 'fa-compass'),
    ("INDICATOR", "Indicators", 'fa-area-chart'),
    ("INFORMATIONSOURCE", "Information Portals", 'fa-info-circle'),

    # ("MAPGRAPHDATASET", "Maps, graphs and datasets"),       # replaced by
    # video
    ("VIDEOS", "Videos", 'fa-file-video-o'),

    ("ORGANISATION", "Organisations", 'fa-sitemap'),
    ("DOCUMENT", "Publication and Reports", 'fa-newspaper-o'),
    ("RESEARCHPROJECT", "Research and knowledge projects",
     'research-icon'),
    ("TOOL", "Tools", 'fa-wrench'),

]


class FrontpageSearch(BrowserView):

    # TODO: implement cache using eea.cache
    # @cache
    def _make_link(self, search_type):
        t = {u'function_score':
             {u'query':
              {u'bool':
               {u'filter':
                {u'bool':
                 {u'should':
                  [{u'term': {u'typeOfData': search_type}}]
                  }
                 },
                }
               }
              }
             }

        q = {'query': t}
        l = '/data-and-downloads?source=' + urllib.quote(json.dumps(q))

        return l

    def sections(self):
        catalog = get_tool('portal_catalog')
        counts = {}

        for search_type, _x, _y in SEARCH_TYPES_ICONS:
            count = len(catalog.searchResults(search_type=search_type,
                                              review_state='published'))
            counts[search_type] = count

        return [
            Section(x[1], counts.get(x[0], 0), self._make_link(x[1]), x[2])

            for x in SEARCH_TYPES_ICONS
        ]
