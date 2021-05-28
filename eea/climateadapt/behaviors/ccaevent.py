from zope.schema import (URI, Bool, Choice, Date, Datetime, Int, List, Text,
                         TextLine, Tuple)

from eea.climateadapt import MessageFactory as _
from plone.app.textfield import RichText
from plone.autoform import directives
from z3c.form.interfaces import IAddForm, IEditForm
from plone.namedfile.field import NamedFile

from zope import schema
from plone.supermodel import model
from plone.app.event.dx.interfaces import IDXEvent
from plone.namedfile.field import NamedBlobImage
from plone.autoform.interfaces import IFormFieldProvider
from zope.interface import provider

# TODO: simplify this schema
@provider(IFormFieldProvider)
class ICcaEvent(model.Schema, IDXEvent):
    """ CcaEvent Interface"""
    model.fieldset(
        "cca_event_info",
        label=u"CCA Event details",
        fields=["image", "online_event_url", "participation", "technical_guidance", "online_registration"],
    )

    image = NamedBlobImage(
        title=_(u"Thumbnail"),
        description=_(
            u"Upload a representative picture or logo for the item. "
            u"Recommended size: at least 360/180 px, aspect ratio 2x. "
            u"This image will be used in the search result page - cards view. "
            u"If this image doesn't exist, then the logo image will be used."
        ),
        required=False,
    )

    online_event_url = TextLine(
        title=_(u"Online event URL"), required=True
    )

    technical_guidance  = NamedFile(
        title=_(u"Technical guidance"),
        required=False,
    )

    participation = RichText(
        title=_(u"Participation"),
        required=True,
        default=None
    )

    online_registration = TextLine(
        title=_(u"Online registration"), required=True
    )
