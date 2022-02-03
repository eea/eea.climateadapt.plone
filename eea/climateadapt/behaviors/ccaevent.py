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
from zope.interface import alsoProvides
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField


# TODO: simplify this schema
@provider(IFormFieldProvider)
class ICcaEvent(model.Schema, IDXEvent):
    """ CcaEvent Interface"""
    model.fieldset(
        "cca_event_info",
        label=u"CCA Event details",
        fields=[
            "image",
            "subtitle",
            "online_event_url",
            "agenda_file",
            "agenda",
            "background_documents",
            "participation",
            #"technical_guidance",
            "language",
            "online_registration",
            "online_registration_message",
            "online_registration_documents",
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

    subtitle = TextLine(
        title=_(u"Subtitle"), required=False
    )

    online_event_url = TextLine(
        title=_(u"More information on the event (URL)"), required=False
    )

    agenda = RichText(
        title=_(u"Agenda"),
        required=False,
        default=None
     )

    agenda_file = NamedFile(
        title=_(u"Agenda document"),
        required=False,
    )


    background_documents = NamedFile(
        title=_(u"Background documents"),
        required=False,
    )

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
        title=_(u"Online registration (URL)"), required=False
    )

    online_registration_message = RichText(
        title=_(u"Online registration message"),
        required=False,
        default=None
    )

    online_registration_documents = NamedFile(
        title=_(u"Online registration documents"),
        required=False,
    )


alsoProvides(ICcaEvent["image"], ILanguageIndependentField)
alsoProvides(ICcaEvent["online_event_url"], ILanguageIndependentField)
alsoProvides(ICcaEvent["agenda_file"], ILanguageIndependentField)
alsoProvides(ICcaEvent["background_documents"], ILanguageIndependentField)
alsoProvides(ICcaEvent["language"], ILanguageIndependentField)
alsoProvides(ICcaEvent["online_registration"], ILanguageIndependentField)
alsoProvides(ICcaEvent["online_registration_documents"], ILanguageIndependentField)
