from plone import api
from plone.directives import form, dexterity
from plone.namedfile.field import NamedBlobImage
from plone.namedfile.interfaces import IImageScaleTraversable
from eea.climateadapt.interfaces import IEEAClimateAdaptInstalled
from zope.interface import implements
from zope.lifecycleevent import modified
from zope.schema import TextLine
from plone.app.textfield import RichText


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
