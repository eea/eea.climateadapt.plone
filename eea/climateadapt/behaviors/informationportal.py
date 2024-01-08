from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.behaviors.aceitem import IAceItem
from plone.autoform import directives
from z3c.form.interfaces import IAddForm, IEditForm
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField


class IInformationPortal(IAceItem, IBlocks):
    """Information Portal Interface"""

    # directives.omitted(IEditForm, 'year')
    # directives.omitted(IAddForm, 'year')
    directives.omitted(IEditForm, "featured")
    directives.omitted(IAddForm, "featured")

    blocks = JSONField(
        title=_("Blocks"),
        description=_("The JSON representation of the object blocks."),
        schema=BLOCKS_SCHEMA,
        default={
            "1403ed1d-29c5-48d7-9b17-c0e99e4e6893": {
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
            "a2ce2c49-c4af-48ca-ad6f-1d2614346a66": {
            "@type": "title", 
            "copyrightIcon": "ri-copyright-line"
            }, 
            "e42e6013-e16f-493f-8799-58071f3f6799": {
            "@type": "tabs_block", 
            "data": {
                "blocks": {
                "381c3b8f-2fa0-4a6b-b47c-c9b9394f518c": {
                    "@type": "tab", 
                    "blocks": {
                    "1428cfb2-489f-4097-ab8c-6bafac464594": {
                        "@type": "slate"
                    }, 
                    "8a498990-adac-4a1d-ab46-e8676b8951ca": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "02fd2097-cca8-4377-9185-a7ab4d27c15b", 
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
                        "8a498990-adac-4a1d-ab46-e8676b8951ca", 
                        "1428cfb2-489f-4097-ab8c-6bafac464594"
                    ]
                    }, 
                    "title": "Geographic info"
                }, 
                "62868279-32a9-4d85-ba2f-2158886bceae": {
                    "@type": "tab", 
                    "blocks": {
                    "64849075-ac36-4b71-867f-872f640da0b8": {
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
                    "9b8779d5-f46c-4ae9-af4e-6516fc814e86": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "aa6fa216-8985-4621-beb4-1853495efd4d", 
                            "field": {
                            "id": "publication_date", 
                            "title": "Date of item's creation", 
                            "widget": "date"
                            }
                        }, 
                        {
                            "@id": "507f170b-190f-406c-838a-c441e50924e9", 
                            "field": {
                            "id": "title", 
                            "title": "Title", 
                            "widget": "title"
                            }
                        }, 
                        {
                            "@id": "2fca0d39-1515-49ee-8dd6-baeac0e0ab25", 
                            "field": {
                            "id": "description", 
                            "title": "Short summary", 
                            "widget": "description"
                            }
                        }, 
                        {
                            "@id": "43da3678-daf7-4201-aec2-a0ba2786f668", 
                            "field": {
                            "id": "long_description", 
                            "title": "Description", 
                            "widget": "richtext"
                            }
                        }, 
                        {
                            "@id": "fd0a6481-7673-452f-83fd-a077d1508fd0", 
                            "field": {
                            "id": "keywords", 
                            "title": "Keywords", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "51eb6e35-15d5-4191-9f06-f8583dcd48d5", 
                            "field": {
                            "id": "sectors", 
                            "title": "Sectors", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "d145b19d-d4b9-49e3-9106-d827af46a9c0", 
                            "field": {
                            "id": "climate_impacts", 
                            "title": "Climate impacts", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "5c0d82b0-c511-4ca8-ac79-f33ecaf8fed6", 
                            "field": {
                            "id": "elements", 
                            "title": "Adaptation elements", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "e40a86c6-c0ae-423b-801b-0369744895fa", 
                            "field": {
                            "id": "logo", 
                            "title": "Logo", 
                            "widget": "image"
                            }
                        }, 
                        {
                            "@id": "b10e608b-1557-4bfb-bac8-b44bdaf791e7", 
                            "field": {
                            "id": "image", 
                            "title": "Thumbnail", 
                            "widget": "image"
                            }
                        }, 
                        {
                            "@id": "1079c487-63e0-464f-90ea-0095704294d2", 
                            "field": {
                            "id": "origin_website", 
                            "title": "Item from third parties", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "903d3611-5dcc-43ab-a95f-c6f4af5497ba", 
                            "field": {
                            "id": "contributor_list", 
                            "title": "Contributor(s)", 
                            "widget": "relations"
                            }
                        }, 
                        {
                            "@id": "37268112-581b-4fa7-a0b6-d97ebd712e2d", 
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
                        "9b8779d5-f46c-4ae9-af4e-6516fc814e86", 
                        "64849075-ac36-4b71-867f-872f640da0b8"
                    ]
                    }, 
                    "title": "Item Description"
                }, 
                "67e055d0-4264-438e-b1af-c3c770655f65": {
                    "@type": "tab", 
                    "blocks": {
                    "8c2b94eb-95f6-4ee0-ae12-d2edb1dee672": {
                        "@type": "slate"
                    }, 
                    "98505b54-dd56-4639-897a-7ff79cdf10d4": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "b682ba60-7632-49d0-a8da-35e500bf2ac0", 
                            "field": {
                            "id": "include_in_observatory", 
                            "title": "Include in observatory", 
                            "widget": "boolean"
                            }
                        }, 
                        {
                            "@id": "3ff76267-33e6-43e3-a883-f5c01bf269ae", 
                            "field": {
                            "id": "include_in_mission", 
                            "title": "Include in the Mission Portal", 
                            "widget": "boolean"
                            }, 
                            "showLabel": False
                        }, 
                        {
                            "@id": "732a18f5-4df2-40cd-9baa-f0f88f3619cd", 
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
                        "98505b54-dd56-4639-897a-7ff79cdf10d4", 
                        "8c2b94eb-95f6-4ee0-ae12-d2edb1dee672"
                    ]
                    }, 
                    "title": "Inclusion in subsites"
                }, 
                "cbc17c0d-cb4e-440a-92ba-d488a7230122": {
                    "@type": "tab", 
                    "blocks": {
                    "411cf6a3-dba7-42f2-9f48-a2d34d05b884": {
                        "@type": "slate"
                    }, 
                    "9aa36db1-0085-46f9-b6df-2d83a5b6d28f": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "39b4c1d2-f75f-458f-b310-0ab7be9603f2", 
                            "field": {
                            "id": "websites", 
                            "title": "Websites", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "d812ae96-23de-4bff-81fa-af33e5b483b6", 
                            "field": {
                            "id": "source", 
                            "title": "References", 
                            "widget": "richtext"
                            }
                        }, 
                        {
                            "@id": "dd6308a7-7160-40b9-ae41-9c63b09758ee", 
                            "field": {
                            "id": "special_tags", 
                            "title": "Special tagging", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "115c2f6c-b6ff-4ab0-850a-ee8603c65e51", 
                            "field": {
                            "id": "comments", 
                            "title": "Comments", 
                            "widget": "textarea"
                            }
                        }, 
                        {
                            "@id": "24587bad-9b71-4250-8348-1c0c803cf9fd", 
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
                        "9aa36db1-0085-46f9-b6df-2d83a5b6d28f", 
                        "411cf6a3-dba7-42f2-9f48-a2d34d05b884"
                    ]
                    }, 
                    "title": "Reference info"
                }
                }, 
                "blocks_layout": {
                "items": [
                    "62868279-32a9-4d85-ba2f-2158886bceae", 
                    "cbc17c0d-cb4e-440a-92ba-d488a7230122", 
                    "381c3b8f-2fa0-4a6b-b47c-c9b9394f518c", 
                    "67e055d0-4264-438e-b1af-c3c770655f65"
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
                "a2ce2c49-c4af-48ca-ad6f-1d2614346a66", 
                "e42e6013-e16f-493f-8799-58071f3f6799", 
                "1403ed1d-29c5-48d7-9b17-c0e99e4e6893"
            ]
        },
        required=False,
    )