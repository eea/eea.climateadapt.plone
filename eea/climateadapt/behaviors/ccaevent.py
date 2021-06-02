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
        fields=[
            "image",
            "online_event_url",
            "agenda",
            "background_documents",
            "participation",
            "technical_guidance",
            "language",
            "online_registration"
        ],
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
        title=_(u"Online event URL"), required=False
    )

    agenda = RichText(
        title=_(u"Agenda"),
        required=False,
        default=None
    )

    background_documents = NamedFile(
        title=_(u"Background documents"),
        required=False,
    )

    technical_guidance  = NamedFile(
        title=_(u"Technical guidance"),
        required=False,
    )

    #language = TextLine(
    #    title=_(u"Language"), required=False
    #)

    language = Choice(
        title=_(u"Event Language"),
        required=True,
        default='English',
        vocabulary="eea.climateadapt.event_language",
    )

    participation = RichText(
        title=_(u"Participation"),
        required=False,
        default=None
    )

    online_registration = TextLine(
        title=_(u"More information on the event (URL)"), required=False
    )
