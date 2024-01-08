from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.behaviors.aceitem import IAceItem
from plone.autoform import directives
from z3c.form.interfaces import IAddForm, IEditForm
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField

class ITool(IAceItem, IBlocks):
    """Tool Interface"""

    # directives.omitted(IAddForm, 'year')
    # directives.omitted(IEditForm, 'year')
    directives.omitted(IEditForm, "featured")
    directives.omitted(IAddForm, "featured")

    # source = TextLine(title=_(u"Organisation's source"),
    #                  required=False,
    #                  description=u"Describe the original source of the item "
    #                              u"description (250 character limit)")

    blocks = JSONField(
        title=_("Blocks"),
        description=_("The JSON representation of the object blocks."),
        schema=BLOCKS_SCHEMA,
        default={
            "613a783e-8652-410c-b57e-08e96913e0f2": {
            "@type": "tabs_block", 
            "data": {
                "blocks": {
                "796a3ca2-3fd1-41db-a6ff-b28999360212": {
                    "@type": "tab", 
                    "blocks": {
                    "9897e1b5-01a3-4174-b7ec-0624f43c9346": {
                        "@type": "slate"
                    }, 
                    "ff371fbc-61bb-4df9-9876-5f8ee9750c94": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "032c01de-aa1e-4b55-a656-b66e3fc8526f", 
                            "field": {
                            "id": "include_in_observatory", 
                            "title": "Include in observatory", 
                            "widget": "boolean"
                            }
                        }, 
                        {
                            "@id": "ae75789f-0ce5-433b-9819-02daf8e34bb5", 
                            "field": {
                            "id": "include_in_mission", 
                            "title": "Include in the Mission Portal", 
                            "widget": "boolean"
                            }
                        }, 
                        {
                            "@id": "f0d1c689-f85d-490a-9000-5f14298dddec", 
                            "field": {
                            "id": "health_impacts", 
                            "title": "Health impacts", 
                            "widget": "array"
                            }
                        }
                        ], 
                        "variation": "default"
                    }
                    }, 
                    "blocks_layout": {
                    "items": [
                        "ff371fbc-61bb-4df9-9876-5f8ee9750c94", 
                        "9897e1b5-01a3-4174-b7ec-0624f43c9346"
                    ]
                    }, 
                    "title": "Inclusion in subsites"
                }, 
                "7c25e37c-0502-4970-8102-2529e827af30": {
                    "@type": "tab", 
                    "blocks": {
                    "1c7402ac-d908-4bbf-b712-3c54ccb1d58e": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "04ba1a33-b79b-4bce-b327-d4d2f11e0ce3", 
                            "field": {
                            "id": "geochars", 
                            "title": "Geographic characterisation", 
                            "widget": "textarea"
                            }
                        }
                        ], 
                        "variation": "default"
                    }, 
                    "d9271d2e-372f-4761-b114-7c65de88840a": {
                        "@type": "slate"
                    }
                    }, 
                    "blocks_layout": {
                    "items": [
                        "1c7402ac-d908-4bbf-b712-3c54ccb1d58e", 
                        "d9271d2e-372f-4761-b114-7c65de88840a"
                    ]
                    }, 
                    "title": "Geographic info"
                }, 
                "9d325a25-3493-43a2-8f1d-b26ab911bb91": {
                    "@type": "tab", 
                    "blocks": {
                    "3e6b9302-0683-4a41-9843-5ab6c0e13978": {
                        "@type": "slate"
                    }, 
                    "f3ba3e54-5e62-4283-9283-e391f3411705": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "c9eb933e-4b5a-43ef-825d-a9aad3bb1140", 
                            "field": {
                            "id": "websites", 
                            "title": "Websites", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "bf07141e-942c-41b0-bd58-49e1be179cc6", 
                            "field": {
                            "id": "source", 
                            "title": "References", 
                            "widget": "richtext"
                            }
                        }, 
                        {
                            "@id": "e8b5d353-4868-4d70-b0ff-7dac4e84ac4f", 
                            "field": {
                            "id": "special_tags", 
                            "title": "Special tagging", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "1375eb13-47e5-498c-b7a0-e1420d6fc2ee", 
                            "field": {
                            "id": "comments", 
                            "title": "Comments", 
                            "widget": "textarea"
                            }
                        }, 
                        {
                            "@id": "43f1e56f-b331-437a-862f-7cfd6adbf275", 
                            "field": {
                            "id": "relatedItems", 
                            "title": "Related Items", 
                            "widget": "relations"
                            }
                        }
                        ], 
                        "variation": "default"
                    }
                    }, 
                    "blocks_layout": {
                    "items": [
                        "f3ba3e54-5e62-4283-9283-e391f3411705", 
                        "3e6b9302-0683-4a41-9843-5ab6c0e13978"
                    ]
                    }, 
                    "title": "Reference info"
                }, 
                "d51a9bc2-bf1a-4a44-bb55-6d60cbfa734d": {
                    "@type": "tab", 
                    "blocks": {
                    "6d53b234-46ff-4907-8a5a-f046f4036705": {
                        "@type": "slate"
                    }, 
                    "e771001c-46bb-4bb8-bff1-3727ec852b32": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "d33d00df-e090-4c3b-8a10-e77c1d43bc8c", 
                            "field": {
                            "id": "publication_date", 
                            "title": "Date of item's creation", 
                            "widget": "date"
                            }
                        }, 
                        {
                            "@id": "d1c11d2d-7452-495e-a19d-3b677bab9081", 
                            "field": {
                            "id": "title", 
                            "title": "Title", 
                            "widget": "title"
                            }
                        }, 
                        {
                            "@id": "c101cc6d-1368-4f67-9d39-29dbdc35b839", 
                            "field": {
                            "id": "description", 
                            "title": "Short summary", 
                            "widget": "description"
                            }
                        }, 
                        {
                            "@id": "e229c642-c45b-4556-be8b-a76d0b1dfaf0", 
                            "field": {
                            "id": "long_description", 
                            "title": "Description", 
                            "widget": "richtext"
                            }
                        }, 
                        {
                            "@id": "a34af168-b8bf-42b3-906d-d3f95fcebf25", 
                            "field": {
                            "id": "keywords", 
                            "title": "Keywords", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "86a2172d-54e7-4d3b-8648-c87e2ef4e661", 
                            "field": {
                            "id": "sectors", 
                            "title": "Sectors", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "4825ba9b-a803-479c-8fb1-9169149c117e", 
                            "field": {
                            "id": "climate_impacts", 
                            "title": "Climate impacts", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "7a399cd9-7b68-4127-bc72-1bcc1ec86be2", 
                            "field": {
                            "id": "elements", 
                            "title": "Adaptation elements", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "9390f62c-da9b-46ef-8713-9b9ee95a2e84", 
                            "field": {
                            "id": "logo", 
                            "title": "Logo", 
                            "widget": "image"
                            }
                        }, 
                        {
                            "@id": "68f28cab-e3e9-4926-858a-bd4438f3cb56", 
                            "field": {
                            "id": "image", 
                            "title": "Thumbnail", 
                            "widget": "image"
                            }
                        }, 
                        {
                            "@id": "4648ffd1-85b3-43b9-9089-c8c1ab828c61", 
                            "field": {
                            "id": "origin_website", 
                            "title": "Item from third parties", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "50348533-4cb9-4e8b-9ceb-9024a41aedc0", 
                            "field": {
                            "id": "contributor_list", 
                            "title": "Contributor(s)", 
                            "widget": "relations"
                            }
                        }, 
                        {
                            "@id": "f580799f-61f0-47f4-9fb7-9ffdb39c3adb", 
                            "field": {
                            "id": "other_contributor", 
                            "title": "Other contributor(s)", 
                            "widget": "textarea"
                            }
                        }
                        ], 
                        "variation": "default"
                    }
                    }, 
                    "blocks_layout": {
                    "items": [
                        "e771001c-46bb-4bb8-bff1-3727ec852b32", 
                        "6d53b234-46ff-4907-8a5a-f046f4036705"
                    ]
                    }, 
                    "title": "Item Description"
                }
                }, 
                "blocks_layout": {
                "items": [
                    "d51a9bc2-bf1a-4a44-bb55-6d60cbfa734d", 
                    "9d325a25-3493-43a2-8f1d-b26ab911bb91", 
                    "7c25e37c-0502-4970-8102-2529e827af30", 
                    "796a3ca2-3fd1-41db-a6ff-b28999360212"
                ]
                }
            }, 
            "template": "default", 
            "verticalAlign": "flex-start"
            }, 
            "72eff79b-8c00-44f1-98b9-16fcca2a3f03": {
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
            "96854e5f-1b23-484a-b009-d3a8523b2b43": {
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
                "96854e5f-1b23-484a-b009-d3a8523b2b43", 
                "613a783e-8652-410c-b57e-08e96913e0f2", 
                "72eff79b-8c00-44f1-98b9-16fcca2a3f03"
            ]
        },
        required=False,
    )
