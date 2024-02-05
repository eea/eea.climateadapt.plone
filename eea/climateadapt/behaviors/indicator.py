from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.behaviors.aceitem import IAceItem
from plone.autoform import directives
from z3c.form.interfaces import IAddForm, IEditForm
from zope.schema import Date, Text
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField


class IIndicator(IAceItem, IBlocks):
    """ Indicator Interface"""

    # directives.omitted(IEditForm, 'year')
    # directives.omitted(IAddForm, 'year')
    directives.omitted(IEditForm, "featured")
    directives.omitted(IAddForm, "featured")

    map_graphs = Text(title=_(u"Map/Graphs"), required=False)

    publication_date = Date(
        title=_(u"Date of item's publication"),
        description=u"The date refers to the latest date of publication of "
        u"the item."
        u" Please use the Calendar icon to add day/month/year. If you want to "
        u"add only the year, please select \"day: 1\", \"month: January\" "
        u"and then the year",
        required=True,
    )

    blocks = JSONField(
        title=_("Blocks"),
        description=_("The JSON representation of the object blocks."),
        schema=BLOCKS_SCHEMA,
        default={
            "44fccbd7-da2f-4fd6-b565-3e7804dd8d52": {
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
            "7bbd49e4-bfcb-46cf-bfd6-2db8749f7a11": {
                "@type": "tabs_block",
                "data": {
                    "blocks": {
                        "25e5959e-f4b8-4a46-b523-56027296968c": {
                            "@type": "tab",
                            "blocks": {
                                "798778c7-e081-42c7-bf5f-08584e3034d5": {
                                    "@type": "metadataSection",
                                    "fields": [
                                        {
                                            "@id": "6a63d9ff-ba70-45fb-a9ca-adc057cb40ea",
                                            "field": {
                                                "id": "websites",
                                                "title": "Websites",
                                                "widget": "array"
                                            }
                                        },
                                        {
                                            "@id": "cf28a9a5-c227-4393-a4eb-c8c0ca7c53b9",
                                            "field": {
                                                "id": "source",
                                                "title": "References",
                                                "widget": "richtext"
                                            }
                                        },
                                        {
                                            "@id": "dc6d7712-7baf-46c6-96c7-5fc69f9c0ec3",
                                            "field": {
                                                "id": "special_tags",
                                                "title": "Special tagging",
                                                "widget": "array"
                                            }
                                        },
                                        {
                                            "@id": "f1872728-e4f4-4a27-bb0b-4098d520cb43",
                                            "field": {
                                                "id": "comments",
                                                "title": "Comments",
                                                "widget": "textarea"
                                            }
                                        },
                                        {
                                            "@id": "2d319998-75df-4072-a486-3c1761c53b03",
                                            "field": {
                                                "id": "relatedItems",
                                                "title": "Related Items",
                                                "widget": "relations"
                                            }
                                        }
                                    ],
                                    "variation": "default"
                                },
                                "c284e0a6-6999-44d1-98e0-971ccdd7f350": {
                                    "@type": "slate"
                                }
                            },
                            "blocks_layout": {
                                "items": [
                                    "798778c7-e081-42c7-bf5f-08584e3034d5",
                                    "c284e0a6-6999-44d1-98e0-971ccdd7f350"
                                ]
                            },
                            "title": "Reference Info"
                        },
                        "28dc71d9-a6c6-4bcd-8014-f29734f1570a": {
                            "@type": "tab",
                            "blocks": {
                                "8020320f-0c8a-43bb-bf05-1ef8411c7a3a": {
                                    "@type": "slate"
                                },
                                "8d25d358-6d84-4d48-8ba7-bace0ddb98e7": {
                                    "@type": "metadataSection",
                                    "fields": [
                                        {
                                            "@id": "9b4329d1-7f8e-4537-a63d-276ea5dd35e2",
                                            "field": {
                                                "id": "geochars",
                                                "title": "Geographic characterisation",
                                                "widget": "textarea"
                                            }
                                        }
                                    ],
                                    "variation": "default"
                                }
                            },
                            "blocks_layout": {
                                "items": [
                                    "8d25d358-6d84-4d48-8ba7-bace0ddb98e7",
                                    "8020320f-0c8a-43bb-bf05-1ef8411c7a3a"
                                ]
                            },
                            "title": "Geographic Info"
                        },
                        "66d0290e-9862-489e-b0ab-ffcbdc858782": {
                            "@type": "tab",
                            "blocks": {
                                "3c143313-5e3c-4b9f-a503-ebea07629392": {
                                    "@type": "metadataSection",
                                    "fields": [
                                        {
                                            "@id": "61913f8b-e5a1-4d91-ae04-560f323cf3bb",
                                            "field": {
                                                "id": "effective",
                                                "title": "Publishing Date",
                                                "widget": "datetime"
                                            }
                                        },
                                        {
                                            "@id": "f29ef125-91de-4cdd-953e-8b3d61880dfe",
                                            "field": {
                                                "id": "expires",
                                                "title": "Expiration Date",
                                                "widget": "datetime"
                                            }
                                        }
                                    ],
                                    "variation": "default"
                                },
                                "6dd89747-194f-4d36-b40a-1ea96cda1136": {
                                    "@type": "slate"
                                }
                            },
                            "blocks_layout": {
                                "items": [
                                    "3c143313-5e3c-4b9f-a503-ebea07629392",
                                    "6dd89747-194f-4d36-b40a-1ea96cda1136"
                                ]
                            },
                            "title": "Dates"
                        },
                        "c3449856-0cbe-497e-bdec-2ba9b191eaec": {
                            "@type": "tab",
                            "blocks": {
                                "3d0c3e80-e2f0-42a3-88dd-358602a875d5": {
                                    "@type": "metadataSection",
                                    "fields": [
                                        {
                                            "@id": "744d9725-309c-4636-a6b3-4e7eaa05d1cb",
                                            "field": {
                                                "id": "include_in_mission",
                                                "title": "Include in the Mission Portal",
                                                "widget": "boolean"
                                            }
                                        },
                                        {
                                            "@id": "8c611ecf-10d1-4d60-ad9b-2896150e4b0d",
                                            "field": {
                                                "id": "include_in_observatory",
                                                "title": "Include in observatory",
                                                "widget": "boolean"
                                            }
                                        },
                                        {
                                            "@id": "94fddc95-7a32-4f4d-bb63-60ddcb76cf95",
                                            "field": {
                                                "id": "health_impacts",
                                                "title": "Health impacts",
                                                "widget": "array"
                                            }
                                        }
                                    ],
                                    "variation": "default"
                                },
                                "9fb96674-da82-4dfb-9d4d-0d5cb817044d": {
                                    "@type": "slate"
                                }
                            },
                            "blocks_layout": {
                                "items": [
                                    "3d0c3e80-e2f0-42a3-88dd-358602a875d5",
                                    "9fb96674-da82-4dfb-9d4d-0d5cb817044d"
                                ]
                            },
                            "title": "Inclusion in the subsites"
                        },
                        "d6ef68a8-f7d9-4e1b-bece-58c499a9055d": {
                            "@type": "tab",
                            "blocks": {
                                "3c2ebb66-f4cf-4228-b1c7-6617e2a49b24": {
                                    "@type": "metadataSection",
                                    "fields": [
                                        {
                                            "@id": "9243cff0-448b-4a00-8ff7-d83c9940e4ea",
                                            "field": {
                                                "id": "publication_date",
                                                "title": "Date of item's publication",
                                                "widget": "date"
                                            }
                                        },
                                        {
                                            "@id": "99979251-95f1-49bc-a315-172cf3d5f1f3",
                                            "field": {
                                                "id": "title",
                                                "title": "Title",
                                                "widget": "title"
                                            }
                                        },
                                        {
                                            "@id": "9456d8f2-23c7-49eb-b219-f3a0b64eb969",
                                            "field": {
                                                "id": "description",
                                                "title": "Short summary",
                                                "widget": "description"
                                            }
                                        },
                                        {
                                            "@id": "1c3acc04-e206-474e-ac80-fa3cb644fc92",
                                            "field": {
                                                "id": "long_description",
                                                "title": "Description",
                                                "widget": "richtext"
                                            }
                                        },
                                        {
                                            "@id": "f6be7cd4-a8fa-4392-80d2-b73e6412cf67",
                                            "field": {
                                                "id": "keywords",
                                                "title": "Keywords",
                                                "widget": "array"
                                            }
                                        },
                                        {
                                            "@id": "e9b6b1f1-198f-4f10-85fb-0ad21af4c714",
                                            "field": {
                                                "id": "sectors",
                                                "title": "Sectors",
                                                "widget": "array"
                                            }
                                        },
                                        {
                                            "@id": "d960fac3-c6e7-4f46-b08f-caca069faadb",
                                            "field": {
                                                "id": "climate_impacts",
                                                "title": "Climate impacts",
                                                "widget": "array"
                                            }
                                        },
                                        {
                                            "@id": "425ae05c-c6d6-4fbc-8f1d-da26959fdc41",
                                            "field": {
                                                "id": "elements",
                                                "title": "Adaptation elements",
                                                "widget": "array"
                                            }
                                        },
                                        {
                                            "@id": "7c085bd7-936b-41ad-ade6-8979d359c2e3",
                                            "field": {
                                                "id": "map_graphs",
                                                "title": "Map/Graphs",
                                                "widget": "textarea"
                                            }
                                        },
                                        {
                                            "@id": "c0dbddd0-c93f-457f-ad86-f3c667f1edc3",
                                            "field": {
                                                "id": "origin_website",
                                                "title": "Item from third parties",
                                                "widget": "array"
                                            }
                                        },
                                        {
                                            "@id": "f360f89d-0958-485a-b49b-dc951e58bc34",
                                            "field": {
                                                "id": "logo",
                                                "title": "Logo",
                                                "widget": "image"
                                            }
                                        },
                                        {
                                            "@id": "5aa26ee2-21a8-41fe-8e25-b50df5a4c257",
                                            "field": {
                                                "id": "image",
                                                "title": "Thumbnail",
                                                "widget": "image"
                                            }
                                        },
                                        {
                                            "@id": "f14044da-c980-470f-934f-c7f487802a94",
                                            "field": {
                                                "id": "contributor_list",
                                                "title": "Contributor(s)",
                                                "widget": "relations"
                                            }
                                        },
                                        {
                                            "@id": "b76b541b-0f79-4802-85fc-5806adc78f84",
                                            "field": {
                                                "id": "other_contributor",
                                                "title": "Other contributor(s)",
                                                "widget": "textarea"
                                            }
                                        }
                                    ],
                                    "variation": "default"
                                },
                                "a3738650-0a77-4d1d-9488-dacbfcc218f7": {
                                    "@type": "slate"
                                }
                            },
                            "blocks_layout": {
                                "items": [
                                    "3c2ebb66-f4cf-4228-b1c7-6617e2a49b24",
                                    "a3738650-0a77-4d1d-9488-dacbfcc218f7"
                                ]
                            },
                            "title": "Item Description"
                        }
                    },
                    "blocks_layout": {
                        "items": [
                            "d6ef68a8-f7d9-4e1b-bece-58c499a9055d",
                            "25e5959e-f4b8-4a46-b523-56027296968c",
                            "28dc71d9-a6c6-4bcd-8014-f29734f1570a",
                            "c3449856-0cbe-497e-bdec-2ba9b191eaec",
                            "66d0290e-9862-489e-b0ab-ffcbdc858782"
                        ]
                    }
                },
                "template": "default",
                "verticalAlign": "flex-start"
            },
            "b0fb074f-9ef6-40b6-b7c8-a5c16df31cb7": {
                "@type": "title",
                "copyrightIcon": "ri-copyright-line"
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
                "b0fb074f-9ef6-40b6-b7c8-a5c16df31cb7",
                "7bbd49e4-bfcb-46cf-bfd6-2db8749f7a11",
                "44fccbd7-da2f-4fd6-b565-3e7804dd8d52"
            ]
        },
        required=False,
    )
