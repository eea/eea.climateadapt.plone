from eea.climateadapt import CcaAdminMessageFactory as _
from plone.app.event.dx.interfaces import IDXEvent
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.textfield import RichText
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.field import NamedBlobImage
from plone.namedfile.field import NamedFile
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField
from plone.supermodel import model
from zope.interface import alsoProvides
from zope.interface import provider
from zope.schema import Choice, TextLine
from .volto_layout import cca_event_blocks, cca_event_items

# from plone.autoform import directives
# from z3c.form.interfaces import IAddForm, IEditForm
# from zope import schema
#URI, Bool, Date, Datetime, Int, List, Text,

# TODO: simplify this schema
@provider(IFormFieldProvider)
class ICcaEvent(model.Schema, IDXEvent, IBlocks):
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
            "event_language",
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

    event_language = Choice(
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

    blocks = JSONField(
        title=_("Blocks"),
        description=_("The JSON representation of the object blocks."),
        schema=BLOCKS_SCHEMA,
        default=cca_event_blocks,
        required=False,
    )

    blocks_layout = JSONField(
        title=_("Blocks Layout"),
        description=_("The JSON representation of the object blocks layout."),
        schema=LAYOUT_SCHEMA,
        default={
            "items": cca_event_items
        },
        required=False,
    )

alsoProvides(ICcaEvent["image"], ILanguageIndependentField)
alsoProvides(ICcaEvent["online_event_url"], ILanguageIndependentField)
alsoProvides(ICcaEvent["agenda_file"], ILanguageIndependentField)
alsoProvides(ICcaEvent["background_documents"], ILanguageIndependentField)
alsoProvides(ICcaEvent["event_language"], ILanguageIndependentField)
alsoProvides(ICcaEvent["online_registration"], ILanguageIndependentField)
alsoProvides(ICcaEvent["online_registration_documents"], ILanguageIndependentField)

from plone.app.event.dx.behaviors import IEventContact

alsoProvides(IEventContact["contact_name"], ILanguageIndependentField)
alsoProvides(IEventContact["contact_email"], ILanguageIndependentField)
alsoProvides(IEventContact["contact_phone"], ILanguageIndependentField)
alsoProvides(IEventContact["event_url"], ILanguageIndependentField)

from plone.app.dexterity.behaviors.metadata import IDublinCore
alsoProvides(IDublinCore["subjects"], ILanguageIndependentField)
alsoProvides(IDublinCore["creators"], ILanguageIndependentField)
alsoProvides(IDublinCore["contributors"], ILanguageIndependentField)
alsoProvides(IDublinCore["rights"], ILanguageIndependentField)

from plone.app.event.dx.behaviors import IEventLocation
alsoProvides(IEventLocation["location"], ILanguageIndependentField)

from plone.app.event.dx.behaviors import IEventBasic
alsoProvides(IEventBasic["start"], ILanguageIndependentField)
alsoProvides(IEventBasic["end"], ILanguageIndependentField)
alsoProvides(IEventBasic["whole_day"], ILanguageIndependentField)
alsoProvides(IEventBasic["open_end"], ILanguageIndependentField)
alsoProvides(IEventBasic["timezone"], ILanguageIndependentField)
alsoProvides(IEventBasic["sync_uid"], ILanguageIndependentField)

from plone.app.versioningbehavior.behaviors import IVersionable
alsoProvides(IVersionable["changeNote"], ILanguageIndependentField)

from plone.app.event.dx.behaviors import IEventRecurrence
alsoProvides(IEventRecurrence["recurrence"], ILanguageIndependentField)

from plone.app.dexterity.behaviors.discussion import IAllowDiscussion
alsoProvides(IAllowDiscussion["allow_discussion"], ILanguageIndependentField)

from plone.app.dexterity.behaviors.exclfromnav import IExcludeFromNavigation
alsoProvides(IExcludeFromNavigation["exclude_from_nav"], ILanguageIndependentField)
