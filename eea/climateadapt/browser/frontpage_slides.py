import json
import urllib
from collections import namedtuple

from zope.interface import implements
from zope.lifecycleevent import modified
from zope.schema import TextLine

from eea.climateadapt.interfaces import IEEAClimateAdaptInstalled
from plone import api
from plone.api.portal import get_tool, getSite
from plone.app.textfield import RichText
from plone.directives import dexterity, form
from plone.memoize import view
from plone.namedfile.field import NamedBlobImage
from plone.namedfile.interfaces import IImageScaleTraversable
from Products.Five.browser import BrowserView


class FrontpageSlideSchema(form.Schema):
    form.fieldset('default',
                  label=u'Item Description',
                  fields=['title', 'long_description',
                          'category', 'read_more_link',
                          ]
                  )

    title = TextLine(title=(u"Title"),
                     description=u"Item Name (250 character limit)",
                     required=True)

    long_description = RichText(title=(u"Description"),
                                description=u"Provide a description of the "
                                u"item.(5,000 character limit)",
                                required=True)

    category = TextLine(title=(u"Category"),
                        description=u"Slider thumbnail title. "
                        u"Keep it short (25 character limit)",
                        required=True)

    read_more_link = TextLine(title=u"Read more link",
                              required=False)


class IFrontpageSlide(FrontpageSlideSchema):
    """ Interface for the FrontapgeSlide content type """


class FrontpageSlide(dexterity.Container):
    """ Slide content type for which the richtext behavior is activated """
    implements(IFrontpageSlide, IEEAClimateAdaptInstalled)


class FrontpageSlidesView (BrowserView):
    """ BrowserView for the frontpage slides which will be loaded through diazo
    """

    def __call__(self):
        site = api.portal.get()
        sf = site.unrestrictedTraverse('/cca/frontpage-slides')
        slides = [o for o in sf.contentValues()
                  if api.content.get_state(o) == 'published']
        images = []

        for slide in slides:
            handler = getattr(self, 'handle_' + slide.title.encode(), None)
            slide_data = {}

            image_url, copyright = self.getImages(slide)

            if handler:
                slide_data = handler(slide)
            else:
                slide_data = {
                    'image_url': image_url,
                    'copyright': copyright,
                    'title': slide.title,
                    'description': slide.long_description,
                    'category': slide.category,
                    'url': slide.read_more_link
                }
            images.append(slide_data)
        self.images = images

        return self.index()

    @view.memoize
    def getCurrentDate(self):
        import datetime
        return datetime.datetime.now()

    def getImages(self, slide):
        images = [image.getObject() for image in slide.getFolderContents()]

        if len(images) is 0:
            return ''

        now = self.getCurrentDate()
        try:
            image = images[now.day / 7]
        except:
            image = images[-1]

        url = image.absolute_url() + "/@@images/image/fp-slide"
        copyright = image.rights

        return url, copyright

    def getDescription(self, image):
        description = image.get('description', '')

        if hasattr(description, 'output'):
            return self.html2text(description.output)
        else:
            return description

    def handle_news_items(self, slide):
        """ Gets the most recent updated news/events item"""
        site = getSite()
        catalog = site.portal_catalog
        result = catalog.searchResults({'portal_type': ['News Item', 'Event'],
                                        'review_state': 'published',
                                        'sort_on': 'effective',
                                        'sort_order': 'reverse'},
                                       full_objects=True)[0]

        news = result.getObject()

        image_url, copyright = self.getImages(slide)

        return {
            'image_url': image_url,
            'copyright': copyright,
            'title': news.Title(),
            'description': news.description,
            'category': 'Latest <br/> News & Events',
            'url': news.absolute_url(),
        }

    def handle_last_casestudy(self, slide):
        """ Gets the most recent updated casestudy"""
        site = getSite()
        catalog = site.portal_catalog
        brain = catalog.searchResults({
            'portal_type': 'eea.climateadapt.casestudy',
            'review_state': 'published',
            'sort_on': 'effective',
            'sort_order': 'descending',
        }, full_objects=True)[0]

        cs = brain.getObject()

        image_url, copyright = self.getImages(slide)

        return {
            'image_url': image_url,
            'copyright': copyright,
            'title': cs.Title(),
            'description': cs.long_description,
            'category': 'Most recent <br/> Case Study',
            'url': cs.absolute_url(),
        }

    @view.memoize
    def html2text(self, html):
        if not isinstance(html, basestring):
            return u""
        portal_transforms = api.portal.get_tool(name='portal_transforms')
        data = portal_transforms.convertTo('text/plain',
                                           html, mimetype='text/html')
        text = data.getData()

        return text

    # Currently UNUSED
    # def handle_last_dbitem(self, slide):
    #     """ Gets the most recent updated aceitem"""
    #     site = getSite()
    #     catalog = site.portal_catalog
    #     result = catalog.searchResults({
    #         'portal_type': [
    #             'eea.climateadapt.informationportal',
    #             'eea.climateadapt.guidancedocument',
    #             'eea.climateadapt.tool',
    #             'eea.climateadapt.mapgraphdataset',
    #             'eea.climateadapt.indicator',
    #             'eea.climateadapt.organisation'
    #         ],
    #         'review_state': 'published',
    #         'sort_by': 'effective'}, full_objects=True)[0]
    #
    #     db_item = result.getObject()
    #
    #     return {
    #         'image':
    #         "/++resource++eea.climateadapt/frontpage/aceitem_picture.jpg",
    #         'title': db_item.Title(),
    #         'description': db_item.long_description,
    #         'category': 'Database item',
    #         'url': db_item.absolute_url(),
    #     }

    def handle_last_publication(self, slide):
        """ Gets the most recent updated publication and report"""
        site = getSite()
        catalog = site.portal_catalog
        result = catalog.searchResults({
            'portal_type': 'eea.climateadapt.publicationreport',
            'review_state': 'published',
            'sort_on': 'effective',
            'sort_order': 'descending',
        }, full_objects=True)[0]

        publi = result.getObject()

        image_url, copyright = self.getImages(slide)

        return {
            'image_url': image_url,
            'copyright': copyright,
            'title': publi.Title(),
            'description': publi.long_description,
            'category': 'Most recent <br/> Publication or Report',
            'url': publi.absolute_url(),
        }


Section = namedtuple('Section',
                     ['title', 'count', 'link', 'icon_class'])

SEARCH_TYPES_ICONS = [
    ("MEASURE", "Adaptation options", 'fa-cogs'),
    ("ACTION", "Case studies", 'fa-file-text-o'),
    ("GUIDANCE", "Guidance", 'fa-compass'),
    ("INDICATOR", "Indicators", 'fa-area-chart'),
    ("INFORMATIONSOURCE", "Information portals", 'fa-info-circle'),

    # ("MAPGRAPHDATASET", "Maps, graphs and datasets"),       # replaced by
    # video
    ("VIDEO", "Videos", 'fa-file-video-o'),

    ("ORGANISATION", "Organisations", 'fa-sitemap'),
    ("DOCUMENT", "Publications and reports", 'fa-newspaper-o'),
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
