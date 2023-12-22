from zope.interface import alsoProvides
from zope.schema import Date

from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.behaviors.aceitem import IAceItem
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.autoform import directives
from z3c.form.interfaces import IAddForm, IEditForm
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField

class IPublicationReport(IAceItem, IBlocks):
    """Publication Report Interface"""

    # directives.omitted(IEditForm, 'year')
    # directives.omitted(IAddForm, 'year')
    directives.omitted(IEditForm, "featured")
    directives.omitted(IAddForm, "featured")

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
            "87949dc6-ca21-4f7c-8dc9-f0a599b106d3": {
            "@type": "slate"
            }, 
            "aef32685-1aaf-440f-b48b-3379da51ef74": {
            "@type": "tabs_block", 
            "data": {
                "blocks": {
                "0bc447c1-e867-46df-90dd-5a085665b1f6": {
                    "@type": "tab", 
                    "blocks": {
                    "794f2ccf-edb4-4086-9af7-6185c2086708": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "9670328d-b367-4c80-bebb-b6c062fdbe14", 
                            "field": {
                            "id": "publication_date", 
                            "title": "Date of item's publication", 
                            "widget": "date"
                            }
                        }, 
                        {
                            "@id": "bf893209-1f93-4301-98d8-69ce308448d8", 
                            "field": {
                            "id": "title", 
                            "title": "Title", 
                            "widget": "title"
                            }
                        }, 
                        {
                            "@id": "a394626e-6ac4-4e64-8779-12323049c856", 
                            "field": {
                            "id": "description", 
                            "title": "Short summary", 
                            "widget": "description"
                            }
                        }, 
                        {
                            "@id": "1de9ae1c-4faf-4a6e-966d-6f6f4554fa5f", 
                            "field": {
                            "id": "long_description", 
                            "title": "Description", 
                            "widget": "richtext"
                            }
                        }, 
                        {
                            "@id": "153f23dd-933e-45ad-9066-2b6753b21346", 
                            "field": {
                            "id": "keywords", 
                            "title": "Keywords", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "68615032-0585-4e25-b36d-4500ea7334e5", 
                            "field": {
                            "id": "sectors", 
                            "title": "Sectors", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "8bc5432b-1c9c-4be2-a5a8-f0d97c56aeff", 
                            "field": {
                            "id": "climate_impacts", 
                            "title": "Climate impacts", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "ddbdb253-cca9-4f03-bd9e-d2ecd4c54110", 
                            "field": {
                            "id": "elements", 
                            "title": "Adaptation elements", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "d267ea61-bd30-46e7-9709-896da834b303", 
                            "field": {
                            "id": "logo", 
                            "title": "Logo", 
                            "widget": "image"
                            }
                        }, 
                        {
                            "@id": "3886e6b8-0fef-4d31-a4fc-261266531b66", 
                            "field": {
                            "id": "image", 
                            "title": "Thumbnail", 
                            "widget": "image"
                            }
                        }, 
                        {
                            "@id": "dd2822cf-1892-4c5c-9881-c0ad1a67ff30", 
                            "field": {
                            "id": "origin_website", 
                            "title": "Item from third parties", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "4af85da4-3c32-4e75-b56e-393e3704ef4c", 
                            "field": {
                            "id": "contributor_list", 
                            "title": "Contributor(s)", 
                            "widget": "relations"
                            }
                        }, 
                        {
                            "@id": "43aa3122-e220-4455-ba31-2b4a278d66a4", 
                            "field": {
                            "id": "other_contributor", 
                            "title": "Other contributor(s)", 
                            "widget": "textarea"
                            }
                        }
                        ], 
                        "variation": "default"
                    }, 
                    "fef8785a-a894-4ec9-95a8-f3fd57a57578": {
                        "@type": "slate"
                    }
                    }, 
                    "blocks_layout": {
                    "items": [
                        "794f2ccf-edb4-4086-9af7-6185c2086708", 
                        "fef8785a-a894-4ec9-95a8-f3fd57a57578"
                    ]
                    }, 
                    "title": "Item description"
                }, 
                "11094ac9-d04c-45f2-8b69-5e0f2054c450": {
                    "@type": "tab", 
                    "blocks": {
                    "065ade50-40f6-4361-b7db-f7fc5d4d0ce3": {
                        "@type": "slate"
                    }, 
                    "8fc54b45-d282-45e2-ae1f-d5dcd1608be4": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "d2252de2-0226-408b-bc14-7eef12e125d1", 
                            "field": {
                            "id": "websites", 
                            "title": "Websites", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "2e6e2b03-8aaf-40af-84fc-1783d14afa25", 
                            "field": {
                            "id": "source", 
                            "title": "References", 
                            "widget": "richtext"
                            }
                        }, 
                        {
                            "@id": "d79fc04d-ea8f-46ef-b576-387e342c69ee", 
                            "field": {
                            "id": "special_tags", 
                            "title": "Special tagging", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "eb06b267-6a00-40b9-86cb-eda08c3aae2f", 
                            "field": {
                            "id": "comments", 
                            "title": "Comments", 
                            "widget": "textarea"
                            }
                        }, 
                        {
                            "@id": "a476f18e-2d27-4eb1-9793-6581c8ab78da", 
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
                        "8fc54b45-d282-45e2-ae1f-d5dcd1608be4", 
                        "065ade50-40f6-4361-b7db-f7fc5d4d0ce3"
                    ]
                    }, 
                    "title": "Reference info"
                }, 
                "3e1c86fb-29b8-4606-9671-94f4e18bf951": {
                    "@type": "tab", 
                    "blocks": {
                    "210fc730-b795-4002-a5f0-9c0fba7200c4": {
                        "@type": "slate"
                    }, 
                    "eaa796a3-ab2a-4684-86ea-fd8a74542dda": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "412c26c9-ca67-4622-b9aa-f1fa4c7bbab2", 
                            "field": {
                            "id": "include_in_observatory", 
                            "title": "Include in observatory", 
                            "widget": "boolean"
                            }
                        }, 
                        {
                            "@id": "d505c418-6650-43d8-a81c-f126797a26ef", 
                            "field": {
                            "id": "include_in_mission", 
                            "title": "Include in the Mission Portal", 
                            "widget": "boolean"
                            }
                        }, 
                        {
                            "@id": "e424bf22-2c39-4ebe-b52f-98fe8059e8da", 
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
                        "eaa796a3-ab2a-4684-86ea-fd8a74542dda", 
                        "210fc730-b795-4002-a5f0-9c0fba7200c4"
                    ]
                    }, 
                    "title": "Include in subsites"
                }, 
                "c405ddc3-596c-47c1-9cf4-2f59aa4f214e": {
                    "@type": "tab", 
                    "blocks": {
                    "96058a9b-5c97-45c8-a5c5-c8d5dff5bcb3": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "23831f33-c740-4ad4-a413-46e642e88070", 
                            "field": {
                            "id": "geochars", 
                            "title": "Geographic characterisation", 
                            "widget": "textarea"
                            }
                        }
                        ], 
                        "variation": "default"
                    }, 
                    "bba516ef-c34b-45ef-b1cc-1eecc154f433": {
                        "@type": "slate"
                    }
                    }, 
                    "blocks_layout": {
                    "items": [
                        "96058a9b-5c97-45c8-a5c5-c8d5dff5bcb3", 
                        "bba516ef-c34b-45ef-b1cc-1eecc154f433"
                    ]
                    }, 
                    "title": "Geographic info"
                }
                }, 
                "blocks_layout": {
                "items": [
                    "0bc447c1-e867-46df-90dd-5a085665b1f6", 
                    "11094ac9-d04c-45f2-8b69-5e0f2054c450", 
                    "c405ddc3-596c-47c1-9cf4-2f59aa4f214e", 
                    "3e1c86fb-29b8-4606-9671-94f4e18bf951"
                ]
                }
            }, 
            "template": "default", 
            "verticalAlign": "flex-start"
            }, 
            "bfac63ff-6a8c-435c-aad9-32f157903402": {
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
                "bfac63ff-6a8c-435c-aad9-32f157903402", 
                "aef32685-1aaf-440f-b48b-3379da51ef74", 
                "87949dc6-ca21-4f7c-8dc9-f0a599b106d3"
            ]
        },
        required=False,
    )


alsoProvides(IPublicationReport["publication_date"], ILanguageIndependentField)
