from zope.schema import Text, TextLine, Date
from zope.interface import alsoProvides
from eea.climateadapt import CcaAdminMessageFactory as _

from .aceitem import IAceItem
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.textfield import RichText

from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField


class IAceVideo(IAceItem, IBlocks):
    """Video schema"""

    embed_url = TextLine(
        title=_(u"Video URL"), description=u"Enter the video URL", required=True
    )

    video_height = TextLine(
        title=_(u"Video Height"),
        description=u"Enter the video height",
        required=False,
        default=u"480",
    )

    publication_date = Date(
        title=_(u"Date of video's release"),
        description=u"The date refers to the moment in which the video has "
        u"been released. Please use the Calendar icon to add day/month/year. "
        u"If you want to add only the year, please select \"day: 1\", "
        u"\"month: January\" and then the year",
        required=True,
    )

    related_documents_presentations = RichText(
        title=_(u"Related documents and presentations"),
        required=False,
        default=None
    )

    blocks = JSONField(
        title=_("Blocks"),
        description=_("The JSON representation of the object blocks."),
        schema=BLOCKS_SCHEMA,
        default={
            "2fd06a1a-25dc-49fc-a032-e377a676806b": {
            "@type": "title", 
            "copyrightIcon": "ri-copyright-line"
            }, 
            "5c1c7869-b4bd-4de6-ac89-8f145846c929": {
            "@type": "tabs_block", 
            "data": {
                "blocks": {
                "01f426db-0c8f-460a-82db-daf84b6d2ec5": {
                    "@type": "tab", 
                    "blocks": {
                    "9b9f5a2c-b9b2-4156-a8dd-d041e3764ac3": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "87b0ed3e-331f-4cb2-b4f6-cd1816b14507", 
                            "field": {
                            "id": "websites", 
                            "title": "Websites", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "bc7d44e1-cf49-41ee-a438-93aaa61eb3dd", 
                            "field": {
                            "id": "source", 
                            "title": "References", 
                            "widget": "richtext"
                            }
                        }, 
                        {
                            "@id": "23714626-92a6-41eb-aaa1-8dd8e8da41c7", 
                            "field": {
                            "id": "special_tags", 
                            "title": "Special tagging", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "4ca824d2-25c9-493a-96a7-808437814247", 
                            "field": {
                            "id": "comments", 
                            "title": "Comments", 
                            "widget": "textarea"
                            }
                        }
                        ], 
                        "variation": "default"
                    }, 
                    "a92e340f-959f-4b35-ba5d-c91fed183148": {
                        "@type": "slate"
                    }
                    }, 
                    "blocks_layout": {
                    "items": [
                        "9b9f5a2c-b9b2-4156-a8dd-d041e3764ac3", 
                        "a92e340f-959f-4b35-ba5d-c91fed183148"
                    ]
                    }, 
                    "title": "Reference info"
                }, 
                "87dcd7a3-02be-46aa-80fc-60296cff1d4f": {
                    "@type": "tab", 
                    "blocks": {
                    "b0e83fc5-62d7-492e-8158-c34d65f04d37": {
                        "@type": "slate"
                    }, 
                    "b75ec765-8c1e-4a55-82eb-59762a4477be": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "a0226dc9-5232-4f7f-82fe-86be53ed99f0", 
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
                        "b75ec765-8c1e-4a55-82eb-59762a4477be", 
                        "b0e83fc5-62d7-492e-8158-c34d65f04d37"
                    ]
                    }, 
                    "title": "Geographic info"
                }, 
                "979a324c-624b-43dc-84ab-31d7084de67a": {
                    "@type": "tab", 
                    "blocks": {
                    "0a83446f-d0d9-41ab-8884-5a5e7dc41b12": {
                        "@type": "slate"
                    }, 
                    "667ff441-5cec-4d61-a7b0-c0230cbe67c8": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "c6720af7-0e89-4b07-a0b5-aaad1d49acc6", 
                            "field": {
                            "id": "include_in_observatory", 
                            "title": "Include in observatory", 
                            "widget": "boolean"
                            }
                        }, 
                        {
                            "@id": "e6e419f8-31b3-4738-b1ff-8958f663a107", 
                            "field": {
                            "id": "include_in_mission", 
                            "title": "Include in the Mission Portal", 
                            "widget": "boolean"
                            }
                        }, 
                        {
                            "@id": "c0c5a8d9-a06e-4fb5-ab3f-c6facd60e77d", 
                            "field": {
                            "id": "health_impacts", 
                            "title": "Health impacts", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "6240962b-7933-44bc-8a05-762286a43755", 
                            "field": {
                            "id": "relatedItems", 
                            "title": "Related Items", 
                            "widget": "relations"
                            }, 
                            "hideInView": False
                        }
                        ], 
                        "variation": "default"
                    }
                    }, 
                    "blocks_layout": {
                    "items": [
                        "667ff441-5cec-4d61-a7b0-c0230cbe67c8", 
                        "0a83446f-d0d9-41ab-8884-5a5e7dc41b12"
                    ]
                    }, 
                    "title": "Inclusion in subsites"
                }, 
                "9c9c24e8-1f8c-4f11-9e44-a5c4769beb6d": {
                    "@type": "tab", 
                    "blocks": {
                    "3191a23f-1835-4ffd-98ce-8e38f10c8901": {
                        "@type": "slate"
                    }, 
                    "319a868c-d713-40a8-963b-288c82e3397f": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "a49581e1-6772-4846-b68a-66d529fb8716", 
                            "field": {
                            "id": "id", 
                            "title": "Short name", 
                            "widget": "string"
                            }
                        }
                        ], 
                        "variation": "default"
                    }
                    }, 
                    "blocks_layout": {
                    "items": [
                        "319a868c-d713-40a8-963b-288c82e3397f", 
                        "3191a23f-1835-4ffd-98ce-8e38f10c8901"
                    ]
                    }, 
                    "title": "Settings"
                }, 
                "fd91f1d7-3499-4473-bd12-646a9129503b": {
                    "@type": "tab", 
                    "blocks": {
                    "1ee28778-69d8-4e7f-944a-8efdf702b12a": {
                        "@type": "slate"
                    }, 
                    "6d1306eb-fb93-4e84-9c58-14636394851e": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "758e962f-acf1-46d4-b003-a8d8855efb67", 
                            "field": {
                            "id": "publication_date", 
                            "title": "Date of video's release", 
                            "widget": "date"
                            }
                        }, 
                        {
                            "@id": "46d570fd-98bf-4341-92c8-7edf2b24bc15", 
                            "field": {
                            "id": "video_height", 
                            "title": "Video Height", 
                            "widget": "string"
                            }
                        }, 
                        {
                            "@id": "de478a87-1560-4657-ada5-bc5cc03f71ee", 
                            "field": {
                            "id": "embed_url", 
                            "title": "Video URL", 
                            "widget": "string"
                            }
                        }, 
                        {
                            "@id": "9745a47e-697a-4f44-b66b-1739c5ea3941", 
                            "field": {
                            "id": "title", 
                            "title": "Title", 
                            "widget": "title"
                            }
                        }, 
                        {
                            "@id": "d644afa3-38d9-4d2b-97cb-3ccdec374c4a", 
                            "field": {
                            "id": "description", 
                            "title": "Short summary", 
                            "widget": "description"
                            }
                        }, 
                        {
                            "@id": "452cd1ea-2cea-4f50-8f2f-1c3631df54cb", 
                            "field": {
                            "id": "long_description", 
                            "title": "Description", 
                            "widget": "richtext"
                            }
                        }, 
                        {
                            "@id": "7984b59a-83f9-4c5b-a78c-ed551e9d00fc", 
                            "field": {
                            "id": "keywords", 
                            "title": "Keywords", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "ad014d41-5315-4222-a085-bd3a3c70ed43", 
                            "field": {
                            "id": "sectors", 
                            "title": "Sectors", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "cbefd4d3-22ca-4021-9812-52b4af844754", 
                            "field": {
                            "id": "climate_impacts", 
                            "title": "Climate impacts", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "39b01189-4de8-4b84-ad63-170714d136f6", 
                            "field": {
                            "id": "elements", 
                            "title": "Adaptation elements", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "da17b7b4-01b9-4098-84ac-c3b69124514b", 
                            "field": {
                            "id": "logo", 
                            "title": "Logo", 
                            "widget": "image"
                            }
                        }, 
                        {
                            "@id": "023c96b1-e3d9-43d8-9416-f72e4d4ec03e", 
                            "field": {
                            "id": "image", 
                            "title": "Thumbnail", 
                            "widget": "image"
                            }
                        }, 
                        {
                            "@id": "2d39bd5c-69b7-49ff-9829-7d6ec50bf002", 
                            "field": {
                            "id": "origin_website", 
                            "title": "Item from third parties", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "79a785ca-68c5-413c-bb38-466555bdb451", 
                            "field": {
                            "id": "contributor_list", 
                            "title": "Contributor(s)", 
                            "widget": "relations"
                            }
                        }, 
                        {
                            "@id": "909c32e9-ac82-496b-9c1b-5c79e9a25db9", 
                            "field": {
                            "id": "other_contributor", 
                            "title": "Other contributor(s)", 
                            "widget": "textarea"
                            }
                        }, 
                        {
                            "@id": "67f9a021-fdc7-469b-953f-0e483a692323", 
                            "field": {
                            "id": "related_documents_presentations", 
                            "title": "Related documents and presentations", 
                            "widget": "richtext"
                            }
                        }
                        ], 
                        "variation": "default"
                    }
                    }, 
                    "blocks_layout": {
                    "items": [
                        "6d1306eb-fb93-4e84-9c58-14636394851e", 
                        "1ee28778-69d8-4e7f-944a-8efdf702b12a"
                    ]
                    }, 
                    "title": "Item description"
                }
                }, 
                "blocks_layout": {
                "items": [
                    "fd91f1d7-3499-4473-bd12-646a9129503b", 
                    "01f426db-0c8f-460a-82db-daf84b6d2ec5", 
                    "87dcd7a3-02be-46aa-80fc-60296cff1d4f", 
                    "979a324c-624b-43dc-84ab-31d7084de67a", 
                    "9c9c24e8-1f8c-4f11-9e44-a5c4769beb6d"
                ]
                }
            }, 
            "template": "default", 
            "verticalAlign": "flex-start"
            }, 
            "99df1833-612c-42c8-b847-facf75786c44": {
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
                "2fd06a1a-25dc-49fc-a032-e377a676806b", 
                "5c1c7869-b4bd-4de6-ac89-8f145846c929", 
                "99df1833-612c-42c8-b847-facf75786c44"
            ]
        },
        required=False,
    )

alsoProvides(IAceVideo["embed_url"], ILanguageIndependentField)
alsoProvides(IAceVideo["video_height"], ILanguageIndependentField)
alsoProvides(IAceVideo["publication_date"], ILanguageIndependentField)
alsoProvides(IAceVideo["related_documents_presentations"], ILanguageIndependentField)
