from zope.interface import alsoProvides
from zope.schema import Date

from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.behaviors.aceitem import IAceItem
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.autoform import directives
from z3c.form.interfaces import IAddForm, IEditForm
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField


class IGuidanceDocument(IAceItem, IBlocks):
    """Guidance Document Interface"""

    directives.omitted(IEditForm, "featured")
    directives.omitted(IAddForm, "featured")
    # directives.omitted(IEditForm, 'year')
    # directives.omitted(IAddForm, 'year')

    publication_date = Date(
        title=_(u"Date of item's publication"),
        description=u"The date refers to the latest date of publication"
        u" of the item (different from the date of item's"
        u" publication in Climate ADAPT)."
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
            "02958cd6-97c8-42a2-8cf9-cc50379d77c7": {
            "@type": "tabs_block", 
            "data": {
                "blocks": {
                "2d3795ad-fb5f-4de6-806a-ccc1aa8454b4": {
                    "@type": "tab", 
                    "blocks": {
                    "9bcf7259-5e76-4f3a-ac03-5e47579a50c8": {
                        "@type": "slate"
                    }, 
                    "b226cdc5-d6be-4e7f-9e9d-2b712b212c4e": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "1dc5888a-1c57-44c0-970b-5bcd748d6cd2", 
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
                        "b226cdc5-d6be-4e7f-9e9d-2b712b212c4e", 
                        "9bcf7259-5e76-4f3a-ac03-5e47579a50c8"
                    ]
                    }, 
                    "title": "Geographic info"
                }, 
                "5c6d883f-133e-4cfa-a056-0887c623e4ed": {
                    "@type": "tab", 
                    "blocks": {
                    "4fb588eb-96c0-454b-99f4-3d50661c2721": {
                        "@type": "slate"
                    }, 
                    "a1dcd207-2806-452e-9f8d-614b419117c2": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "6a6acf75-5de7-4f95-9e24-d48eee2bb3ed", 
                            "field": {
                            "id": "include_in_observatory", 
                            "title": "Include in observatory", 
                            "widget": "boolean"
                            }
                        }, 
                        {
                            "@id": "1345cf19-7e56-4b45-90b1-f95e532dca0e", 
                            "field": {
                            "id": "include_in_mission", 
                            "title": "Include in the Mission Portal", 
                            "widget": "boolean"
                            }
                        }, 
                        {
                            "@id": "d2f9c9fe-97b1-47ca-83e4-96625050d4a5", 
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
                        "a1dcd207-2806-452e-9f8d-614b419117c2", 
                        "4fb588eb-96c0-454b-99f4-3d50661c2721"
                    ]
                    }, 
                    "title": "Inclusion in subsites"
                }, 
                "940c762e-d8b5-4b65-bfcb-a28af74b9b4b": {
                    "@type": "tab", 
                    "blocks": {
                    "69c5c473-99c3-4614-8536-886f327201f8": {
                        "@type": "slate"
                    }, 
                    "bca44002-9f20-41ed-ae17-376fbaa69368": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "0d5846ca-de1d-42a9-bd1f-520d3499fbfd", 
                            "field": {
                            "id": "publication_date", 
                            "title": "Date of item's publication", 
                            "widget": "date"
                            }
                        }, 
                        {
                            "@id": "d690b90e-3dd3-4755-a680-e9ca872ea7f0", 
                            "field": {
                            "id": "title", 
                            "title": "Title", 
                            "widget": "title"
                            }, 
                            "showLabel": False
                        }, 
                        {
                            "@id": "9bbc91c5-8fa3-4ad9-add4-245f51b41674", 
                            "field": {
                            "id": "description", 
                            "title": "Short summary", 
                            "widget": "description"
                            }
                        }, 
                        {
                            "@id": "4b60344e-b001-4fc9-8da3-bd0089fb1787", 
                            "field": {
                            "id": "long_description", 
                            "title": "Description", 
                            "widget": "richtext"
                            }
                        }, 
                        {
                            "@id": "e131cb87-692d-4864-9ce4-b8b9bbb1b714", 
                            "field": {
                            "id": "keywords", 
                            "title": "Keywords", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "cfff27a1-402b-43d3-8080-ad2ce83acf90", 
                            "field": {
                            "id": "sectors", 
                            "title": "Sectors", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "aa373445-07ee-4752-aa99-cb0b9a18b9fa", 
                            "field": {
                            "id": "climate_impacts", 
                            "title": "Climate impacts", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "7c245917-1622-4dcf-ad37-ff6375264e06", 
                            "field": {
                            "id": "elements", 
                            "title": "Adaptation elements", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "347c88c6-3c37-431b-a3e7-ada15c068d2b", 
                            "field": {
                            "id": "logo", 
                            "title": "Logo", 
                            "widget": "image"
                            }
                        }, 
                        {
                            "@id": "6c1431fa-5e95-41a5-aa04-b281ae11908a", 
                            "field": {
                            "id": "image", 
                            "title": "Thumbnail", 
                            "widget": "image"
                            }
                        }, 
                        {
                            "@id": "7923d2a9-115e-4d34-a239-e53d0c1c87a3", 
                            "field": {
                            "id": "origin_website", 
                            "title": "Item from third parties", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "bca40b94-aa98-4be7-a412-1e89619e434e", 
                            "field": {
                            "id": "contributor_list", 
                            "title": "Contributor(s)", 
                            "widget": "relations"
                            }
                        }, 
                        {
                            "@id": "1b92dc88-cdd7-431a-9109-657a871857da", 
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
                        "bca44002-9f20-41ed-ae17-376fbaa69368", 
                        "69c5c473-99c3-4614-8536-886f327201f8"
                    ]
                    }, 
                    "title": "Item Description"
                }, 
                "941a4acc-7de7-484f-b848-b2e1e5bcf724": {
                    "@type": "tab", 
                    "blocks": {
                    "8b73e4a3-dc96-4287-a8dd-1b5e6c8bd098": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "4086c050-0e46-40b0-8c65-e81f5dc7b077", 
                            "field": {
                            "id": "websites", 
                            "title": "Websites", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "02dd09fb-cbd1-4ba1-b4a8-27d0c286c0d0", 
                            "field": {
                            "id": "source", 
                            "title": "References", 
                            "widget": "richtext"
                            }
                        }, 
                        {
                            "@id": "eaf78bfc-b093-4886-b26e-137ba1e805ec", 
                            "field": {
                            "id": "special_tags", 
                            "title": "Special tagging", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "f2ac2370-7e05-4127-b787-8b3bdf6aa718", 
                            "field": {
                            "id": "comments", 
                            "title": "Comments", 
                            "widget": "textarea"
                            }
                        }, 
                        {
                            "@id": "7da60aa8-229f-4a6b-841b-d697cd679658", 
                            "field": {
                            "id": "relatedItems", 
                            "title": "Related Items", 
                            "widget": "relations"
                            }
                        }
                        ], 
                        "variation": "default"
                    }, 
                    "dc8a63a6-8bf7-485c-9044-c520ca6cfbd3": {
                        "@type": "slate"
                    }
                    }, 
                    "blocks_layout": {
                    "items": [
                        "8b73e4a3-dc96-4287-a8dd-1b5e6c8bd098", 
                        "dc8a63a6-8bf7-485c-9044-c520ca6cfbd3"
                    ]
                    }, 
                    "title": "Reference info"
                }
                }, 
                "blocks_layout": {
                "items": [
                    "940c762e-d8b5-4b65-bfcb-a28af74b9b4b", 
                    "941a4acc-7de7-484f-b848-b2e1e5bcf724", 
                    "2d3795ad-fb5f-4de6-806a-ccc1aa8454b4", 
                    "5c6d883f-133e-4cfa-a056-0887c623e4ed"
                ]
                }
            }, 
            "template": "default", 
            "verticalAlign": "flex-start"
            }, 
            "145aa113-bf4a-4546-9612-864b50e5ab50": {
            "@type": "title", 
            "copyrightIcon": "ri-copyright-line"
            }, 
            "5f508e99-7478-46fb-9fdd-51ca71ba0844": {
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
                "145aa113-bf4a-4546-9612-864b50e5ab50", 
                "02958cd6-97c8-42a2-8cf9-cc50379d77c7", 
                "5f508e99-7478-46fb-9fdd-51ca71ba0844"
            ]
        },
        required=False,
    )


alsoProvides(IGuidanceDocument['publication_date'], ILanguageIndependentField)
