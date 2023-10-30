from zope.schema import (URI, Bool, Choice, Date, Datetime, Int, List, Text,
                         TextLine, Tuple)

from eea.climateadapt import CcaAdminMessageFactory as _
from plone.app.textfield import RichText
from plone.autoform import directives
from z3c.form.interfaces import IAddForm, IEditForm
from plone.namedfile.field import NamedFile
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField

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
        default={
    "1d17872f-06a8-4460-809c-ab14435bafe0": {
        "@type": "title",
        "copyrightIcon": "ri-copyright-line"
    },
    "392b0b2b-85c5-4d36-9c61-262d759b7562": {
        "@type": "slate",
        "plaintext": "",
        "value": [
            {
                "children": [
                    {
                        "text": ""
                    }
                ],
                "type": "p"
            }
        ]
    },
    "8c106f0d-0928-444b-b016-5dd78a2e0eab": {
        "@type": "tabs_block",
        "data": {
            "blocks": {
                "11dbdd53-8d3c-43ec-b04e-b88f4adfe418": {
                    "@type": "tab",
                    "blocks": {
                        "6e994da1-12f3-40df-a92c-f5a26b538d16": {
                            "@type": "slate"
                        },
                        "b03fb0aa-19e4-4bbf-8932-559f0fb22bc3": {
                            "@type": "metadataSection",
                            "fields": [
                                {
                                    "@id": "79063149-0f86-4a38-964f-e47c11235e44",
                                    "field": {
                                        "id": "image",
                                        "title": "Thumbnail",
                                        "widget": "image"
                                    }
                                },
                                {
                                    "@id": "4c73d358-bdb8-4e3f-bd62-f6e20e74a2c5",
                                    "field": {
                                        "id": "subtitle",
                                        "title": "Subtitle",
                                        "widget": "string"
                                    }
                                },
                                {
                                    "@id": "672f0bb5-be52-499c-818c-e272b7663de6",
                                    "field": {
                                        "id": "online_event_url",
                                        "title": "More information on the event (URL)",
                                        "widget": "string"
                                    }
                                },
                                {
                                    "@id": "34b9f17b-ea0b-4204-8f49-d95e3dba572e",
                                    "field": {
                                        "id": "agenda_file",
                                        "title": "Agenda document",
                                        "widget": "file"
                                    }
                                },
                                {
                                    "@id": "fd69fb36-4ee2-4b09-a8d5-4c90e2916e42",
                                    "field": {
                                        "id": "agenda",
                                        "title": "Agenda",
                                        "widget": "richtext"
                                    }
                                },
                                {
                                    "@id": "94cab738-34fc-4a97-9174-84dec751260c",
                                    "field": {
                                        "id": "background_documents",
                                        "title": "Background documents",
                                        "widget": "file"
                                    }
                                },
                                {
                                    "@id": "f32dbee4-5769-468d-a94c-1a6378a638d3",
                                    "field": {
                                        "id": "participation",
                                        "title": "Participation",
                                        "widget": "richtext"
                                    }
                                },
                                {
                                    "@id": "35013a7e-5baa-413e-b483-db45f318789e",
                                    "field": {
                                        "id": "event_language",
                                        "title": "Event Language",
                                        "widget": "choices"
                                    }
                                },
                                {
                                    "@id": "471d9536-bec9-4485-a027-b5e9e1abb29c",
                                    "field": {
                                        "id": "online_registration",
                                        "title": "Online registration (URL)",
                                        "widget": "string"
                                    }
                                },
                                {
                                    "@id": "e3b02ccc-f858-4fb8-a624-dfdf841f8243",
                                    "field": {
                                        "id": "online_registration_message",
                                        "title": "Online registration message",
                                        "widget": "richtext"
                                    }
                                },
                                {
                                    "@id": "91744038-87cd-4910-9efa-da3c0fe895cc",
                                    "field": {
                                        "id": "online_registration_documents",
                                        "title": "Online registration documents",
                                        "widget": "file"
                                    }
                                }
                            ],
                            "variation": "default"
                        }
                    },
                    "blocks_layout": {
                        "items": [
                            "b03fb0aa-19e4-4bbf-8932-559f0fb22bc3",
                            "6e994da1-12f3-40df-a92c-f5a26b538d16"
                        ]
                    },
                    "title": "CCA Event details"
                },
                "1b1914bf-5b46-4baf-95a2-a02df27592e5": {
                    "@type": "tab",
                    "blocks": {
                        "58aa89ca-1c39-4a4d-8226-e53997291468": {
                            "@type": "metadataSection",
                            "fields": [
                                {
                                    "@id": "033d8dbe-5220-46dd-99f6-84906dc5c658",
                                    "field": {
                                        "id": "exclude_from_nav",
                                        "title": "Exclude from navigation",
                                        "widget": "boolean"
                                    }
                                },
                                {
                                    "@id": "1f56769e-0c64-4c2b-b080-803479d79ca7",
                                    "field": {
                                        "id": "allow_discussion",
                                        "title": "Allow discussion",
                                        "widget": "choices"
                                    }
                                },
                                {
                                    "@id": "b06824f1-60aa-454d-b546-6bd0fa17bb94",
                                    "field": {
                                        "id": "id",
                                        "title": "Short name",
                                        "widget": "string"
                                    }
                                }
                            ],
                            "variation": "default"
                        },
                        "ac411770-56de-4cb4-b88e-f762935bec09": {
                            "@type": "slate"
                        }
                    },
                    "blocks_layout": {
                        "items": [
                            "58aa89ca-1c39-4a4d-8226-e53997291468",
                            "ac411770-56de-4cb4-b88e-f762935bec09"
                        ]
                    },
                    "title": "Settings"
                },
                "7138bea1-5a99-469b-afcc-8d9c0e9ec5e1": {
                    "@type": "tab",
                    "blocks": {
                        "68ffaf40-87b1-489f-ade3-fcf3edb5d2f7": {
                            "@type": "metadataSection",
                            "fields": [
                                {
                                    "@id": "b2022a11-20d9-442b-901f-829787e0b93d",
                                    "field": {
                                        "id": "effective",
                                        "title": "Publishing Date",
                                        "widget": "datetime"
                                    }
                                },
                                {
                                    "@id": "cb90c225-e55d-4618-bf65-2c823999fae2",
                                    "field": {
                                        "id": "expires",
                                        "title": "Expiration Date",
                                        "widget": "datetime"
                                    }
                                },
                                {
                                    "@id": "c56e5491-20e9-4102-8f7b-8396f8047224",
                                    "field": {
                                        "id": "timezone",
                                        "title": "Timezone",
                                        "widget": "choices"
                                    }
                                },
                                {
                                    "@id": "92a93414-f7af-477f-bc6d-bdf34d6e60f8",
                                    "field": {
                                        "id": "title",
                                        "title": "Title",
                                        "widget": "title"
                                    }
                                },
                                {
                                    "@id": "fed322f4-abff-4421-b215-09d7b8de50ec",
                                    "field": {
                                        "id": "description",
                                        "title": "Summary",
                                        "widget": "description"
                                    }
                                },
                                {
                                    "@id": "ad98050a-331f-4215-aa0d-7a800ccdf982",
                                    "field": {
                                        "id": "contact_email",
                                        "title": "Contact E-mail",
                                        "widget": "string"
                                    }
                                },
                                {
                                    "@id": "66171230-a4c7-4f49-8662-a3e794cc2614",
                                    "field": {
                                        "id": "event_url",
                                        "title": "Event URL",
                                        "widget": "string"
                                    }
                                },
                                {
                                    "@id": "99361385-8f40-460e-bb2b-93d4323f2643",
                                    "field": {
                                        "id": "location",
                                        "title": "Location",
                                        "widget": "string"
                                    }
                                },
                                {
                                    "@id": "a67c2798-6359-4946-8e08-e29644d73781",
                                    "field": {
                                        "id": "start",
                                        "title": "Event Starts",
                                        "widget": "datetime"
                                    }
                                },
                                {
                                    "@id": "5695d47c-ed32-4dad-83dc-ea6212551323",
                                    "field": {
                                        "id": "end",
                                        "title": "Event Ends",
                                        "widget": "datetime"
                                    }
                                },
                                {
                                    "@id": "807bca1c-70e7-4b4b-856e-1cac4ffada0f",
                                    "field": {
                                        "id": "whole_day",
                                        "title": "Whole Day",
                                        "widget": "boolean"
                                    }
                                },
                                {
                                    "@id": "b5995664-c0fb-405e-a5e9-ff2bdb1cce68",
                                    "field": {
                                        "id": "open_end",
                                        "title": "Open End",
                                        "widget": "boolean"
                                    }
                                },
                                {
                                    "@id": "485f1159-3a96-408b-ab49-78bd22590399",
                                    "field": {
                                        "id": "changeNote",
                                        "title": "Change Note",
                                        "widget": "string"
                                    }
                                },
                                {
                                    "@id": "a0fd54ca-cdf5-4ca5-9bd3-cc1c6fc55b58",
                                    "field": {
                                        "id": "recurrence",
                                        "title": "Recurrence",
                                        "widget": "textarea"
                                    }
                                },
                                {
                                    "@id": "7a66a8e7-70da-42f4-b711-de48f2c97f2e",
                                    "field": {
                                        "id": "text",
                                        "title": "Text",
                                        "widget": "richtext"
                                    }
                                }
                            ],
                            "variation": "default"
                        },
                        "8db9fa99-1e65-45f1-b235-049bc3dbe970": {
                            "@type": "slate"
                        }
                    },
                    "blocks_layout": {
                        "items": [
                            "68ffaf40-87b1-489f-ade3-fcf3edb5d2f7",
                            "8db9fa99-1e65-45f1-b235-049bc3dbe970"
                        ]
                    },
                    "title": "Item Description"
                },
                "ab13d381-3f15-4915-a52b-86b46e544718": {
                    "@type": "tab",
                    "blocks": {
                        "1249ff8d-0fce-4a45-8854-37b22afc2b10": {
                            "@type": "metadataSection",
                            "fields": [
                                {
                                    "@id": "40186598-797f-433b-9bc8-25c283b2f5ff",
                                    "field": {
                                        "id": "subjects",
                                        "title": "Tags",
                                        "widget": "tags"
                                    }
                                },
                                {
                                    "@id": "48ef78c2-b973-41ac-bd8d-43619c939c9e",
                                    "field": {
                                        "id": "relatedItems",
                                        "title": "Related Items",
                                        "widget": "relations"
                                    }
                                }
                            ],
                            "variation": "default"
                        },
                        "3144f1bf-0b12-43fc-892d-21eda18b14e8": {
                            "@type": "slate"
                        }
                    },
                    "blocks_layout": {
                        "items": [
                            "1249ff8d-0fce-4a45-8854-37b22afc2b10",
                            "3144f1bf-0b12-43fc-892d-21eda18b14e8"
                        ]
                    },
                    "title": "Categorization"
                },
                "cb5a1b9b-4aeb-4f81-a67a-55ff9f9c1ff1": {
                    "@type": "tab",
                    "blocks": {
                        "8e923bd7-7b37-4584-bd2e-5ac094fe595d": {
                            "@type": "metadataSection",
                            "fields": [
                                {
                                    "@id": "ace4b99b-3afd-4448-a76a-6262346e1056",
                                    "field": {
                                        "id": "creators",
                                        "title": "Creators",
                                        "widget": "array"
                                    }
                                },
                                {
                                    "@id": "e1d40dfb-0684-426a-b444-0b22c7a41e40",
                                    "field": {
                                        "id": "contributors",
                                        "title": "Contributors",
                                        "widget": "array"
                                    }
                                },
                                {
                                    "@id": "847ec98d-eece-4512-9953-1eb234d59047",
                                    "field": {
                                        "id": "rights",
                                        "title": "Rights",
                                        "widget": "textarea"
                                    }
                                }
                            ],
                            "variation": "default"
                        },
                        "ec71858e-f7ef-465e-ae1f-c3e593266e79": {
                            "@type": "slate"
                        }
                    },
                    "blocks_layout": {
                        "items": [
                            "8e923bd7-7b37-4584-bd2e-5ac094fe595d",
                            "ec71858e-f7ef-465e-ae1f-c3e593266e79"
                        ]
                    },
                    "title": "Ownership"
                }
            },
            "blocks_layout": {
                "items": [
                    "7138bea1-5a99-469b-afcc-8d9c0e9ec5e1",
                    "1b1914bf-5b46-4baf-95a2-a02df27592e5",
                    "ab13d381-3f15-4915-a52b-86b46e544718",
                    "cb5a1b9b-4aeb-4f81-a67a-55ff9f9c1ff1",
                    "11dbdd53-8d3c-43ec-b04e-b88f4adfe418"
                ]
            }
        },
        "template": "default",
        "verticalAlign": "flex-start"
    }
},
        required=False,
    )

    blocks_layout = JSONField(
        title=_("Blocks Layout"),
        description=_("The JSON representation of the object blocks layout."),
        schema=LAYOUT_SCHEMA,
        default={
            "items": [
                "1d17872f-06a8-4460-809c-ab14435bafe0",
                "8c106f0d-0928-444b-b016-5dd78a2e0eab",
                "392b0b2b-85c5-4d36-9c61-262d759b7562"
            ]
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
