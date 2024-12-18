import json

from pkg_resources import resource_filename
from plone.app.dexterity.behaviors.exclfromnav import IExcludeFromNavigation
from plone.app.dexterity.behaviors.discussion import IAllowDiscussion
from plone.app.event.dx.behaviors import IEventRecurrence
from plone.app.versioningbehavior.behaviors import IVersionable
from plone.app.event.dx.behaviors import IEventBasic
from plone.app.event.dx.behaviors import IEventLocation
from plone.app.dexterity.behaviors.metadata import IDublinCore
from plone.app.event.dx.behaviors import IEventContact
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

# from plone.autoform import directives
# from z3c.form.interfaces import IAddForm, IEditForm
# from zope import schema
# URI, Bool, Date, Datetime, Int, List, Text,

fpath = resource_filename(
    "eea.climateadapt.behaviors", "volto_layout_cca_event.json"
)
layout = json.load(open(fpath))


# TODO: simplify this schema
@provider(IFormFieldProvider)
class ICcaEvent(model.Schema, IDXEvent, IBlocks):
    """CcaEvent Interface"""

    # model.fieldset(
    #     "cca_event_info",
    #     label=u"CCA Event details",
    #     fields=[
    #         "image",
    #         "subtitle",
    #         "online_event_url",
    #         "agenda_file",
    #         "agenda",
    #         "background_documents",
    #         "participation",
    #         #"technical_guidance",
    #         "event_language",
    #         "online_registration",
    #         "online_registration_message",
    #         "online_registration_documents",
    #     ],
    # )

    image = NamedBlobImage(
        title=_("Thumbnail"),
        description=_(
            "Upload a representative picture or logo for the item. "
            "Recommended size: at least 360/180 px, aspect ratio 2x. "
            "This image will be used in the search result page - cards view. "
            "If this image doesn't exist, then the logo image will be used."
        ),
        required=False,
    )

    subtitle = TextLine(title=_("Subtitle"), required=False)

    online_event_url = TextLine(
        title=_("More information on the event (URL)"), required=False
    )

    agenda = RichText(title=_("Agenda"), required=False, default=None)

    agenda_file = NamedFile(
        title=_("Agenda document"),
        required=False,
    )

    background_documents = NamedFile(
        title=_("Background documents"),
        required=False,
    )

    event_language = Choice(
        title=_("Event Language"),
        required=True,
        default="English",
        vocabulary="eea.climateadapt.event_language",
    )

    participation = RichText(title=_("Participation"),
                             required=False, default=None)

    online_registration = TextLine(
        title=_("Online registration (URL)"), required=False)

    online_registration_message = RichText(
        title=_("Online registration message"), required=False, default=None
    )

    online_registration_documents = NamedFile(
        title=_("Online registration documents"),
        required=False,
    )

    blocks = JSONField(
        title=_("Blocks"),
        description=_("The JSON representation of the object blocks."),
        schema=BLOCKS_SCHEMA,
        default=layout["blocks"],
        required=False,
    )

    blocks_layout = JSONField(
        title=_("Blocks Layout"),
        description=_("The JSON representation of the object blocks layout."),
        schema=LAYOUT_SCHEMA,
       default=layout["blocks_layout"],
        required=False,
    )


alsoProvides(ICcaEvent["image"], ILanguageIndependentField)
alsoProvides(ICcaEvent["online_event_url"], ILanguageIndependentField)
alsoProvides(ICcaEvent["agenda_file"], ILanguageIndependentField)
alsoProvides(ICcaEvent["background_documents"], ILanguageIndependentField)
alsoProvides(ICcaEvent["event_language"], ILanguageIndependentField)
alsoProvides(ICcaEvent["online_registration"], ILanguageIndependentField)
alsoProvides(ICcaEvent["online_registration_documents"],
             ILanguageIndependentField)


alsoProvides(IEventContact["contact_name"], ILanguageIndependentField)
alsoProvides(IEventContact["contact_email"], ILanguageIndependentField)
alsoProvides(IEventContact["contact_phone"], ILanguageIndependentField)
alsoProvides(IEventContact["event_url"], ILanguageIndependentField)


alsoProvides(IDublinCore["subjects"], ILanguageIndependentField)
alsoProvides(IDublinCore["creators"], ILanguageIndependentField)
alsoProvides(IDublinCore["contributors"], ILanguageIndependentField)
alsoProvides(IDublinCore["rights"], ILanguageIndependentField)


alsoProvides(IEventLocation["location"], ILanguageIndependentField)


alsoProvides(IEventBasic["start"], ILanguageIndependentField)
alsoProvides(IEventBasic["end"], ILanguageIndependentField)
alsoProvides(IEventBasic["whole_day"], ILanguageIndependentField)
alsoProvides(IEventBasic["open_end"], ILanguageIndependentField)
alsoProvides(IEventBasic["timezone"], ILanguageIndependentField)
alsoProvides(IEventBasic["sync_uid"], ILanguageIndependentField)


alsoProvides(IVersionable["changeNote"], ILanguageIndependentField)


alsoProvides(IEventRecurrence["recurrence"], ILanguageIndependentField)


alsoProvides(IAllowDiscussion["allow_discussion"], ILanguageIndependentField)


alsoProvides(
    IExcludeFromNavigation["exclude_from_nav"], ILanguageIndependentField)

IExcludeFromNavigation["exclude_from_nav"].required = False
