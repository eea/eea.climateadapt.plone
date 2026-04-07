import json

from pkg_resources import resource_filename
from plone.app.event.dx.interfaces import IDXEvent
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.textfield import RichText
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.field import NamedBlobImage, NamedFile
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField
from plone.supermodel import model
from zope.interface import alsoProvides, provider
from zope.schema import Choice, TextLine

from eea.climateadapt import CcaAdminMessageFactory as _

fpath = resource_filename("eea.climateadapt.behaviors", "volto_layout_cca_event.json")
layout = json.load(open(fpath))


# TODO: simplify this schema
@provider(IFormFieldProvider)
class ICcaEvent(model.Schema, IDXEvent, IBlocks):
    """CcaEvent Interface"""

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

    # TODO: why is this field not a NamedBlobFile?
    agenda_file = NamedFile(
        title=_("Agenda document"),
        required=False,
    )

    # TODO: why is this field not a NamedBlobFile?
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

    participation = RichText(title=_("Participation"), required=False, default=None)

    online_registration = TextLine(title=_("Online registration (URL)"), required=False)

    online_registration_message = RichText(
        title=_("Online registration message"), required=False, default=None
    )

    # TODO: why is this field not a NamedBlobFile?
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


alsoProvides(ICcaEvent["online_event_url"], ILanguageIndependentField)
alsoProvides(ICcaEvent["event_language"], ILanguageIndependentField)
alsoProvides(ICcaEvent["online_registration"], ILanguageIndependentField)


# blobs are handled by field serializer
# alsoProvides(ICcaEvent["image"], ILanguageIndependentField)

# TODO: this should be made to work with the serialzer
alsoProvides(ICcaEvent["agenda_file"], ILanguageIndependentField)
alsoProvides(ICcaEvent["background_documents"], ILanguageIndependentField)
alsoProvides(ICcaEvent["online_registration_documents"], ILanguageIndependentField)
