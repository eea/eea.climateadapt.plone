from zope.interface import alsoProvides
from zope.schema import (URI, Bool, Choice, Date, Datetime, Int, List, Text,
                         TextLine, Tuple)

from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.behaviors.aceitem import IAceItem
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.namedfile.field import NamedBlobImage
from z3c.form.browser.textlines import TextLinesWidget
from z3c.form.interfaces import IAddForm, IEditForm
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField



class IOrganisation(IAceItem, IBlocks):
    """ Organisation Interface"""

    # directives.omitted(IAddForm, 'year')
    # directives.omitted(IEditForm, 'year')
    directives.omitted(IAddForm, "health_impacts")
    directives.omitted(IEditForm, "health_impacts")
    directives.omitted(IAddForm, "source")
    directives.omitted(IEditForm, "source")
    directives.omitted(IEditForm, "contributor_list")
    directives.omitted(IAddForm, "contributor_list")
    directives.omitted(IEditForm, "featured")
    directives.omitted(IAddForm, "featured")

    acronym = TextLine(
        title=_(u"Acronym"),
        description=_(u"Acronym of the organisation"),
        required=False,
    )

    contact = TextLine(
        title=_(u"Contact"),
        description=_(u"Corporate email or link to contact form"),
        required=True,
    )

    title = TextLine(
        title=_(u"Name"), description=u"Item Name (250 character limit)", required=True
    )

    organisational_key_activities = RichText(
        title=_(u"Key activities within climate change and health"),
        description=u"Please describe the key activities"
        u" undertaken by your organisation that are related"
        u" to the topic of 'climate change and health'."
        u" Please concentrate on activities with most"
        u" direct relevance to the Observatory. You may"
        u" include any hyperlinks to relevant projects in"
        u" the text",
        required=False,
    )

    directives.widget("organisational_links", TextLinesWidget)

    organisational_websites = RichText(
        title=_(u"Links to further information (relevant for the Observatory)"),
        description=u"Please provide a hyperlink to the homepage"
        u' of your organisation in the "Reference'
        u' Information section", here you may also'
        u" provide links to up to two relevant units of"
        u" the organisation that have directly contributed"
        u" to the Observatory and/or up to two hyperlinks"
        u" to relevant networks (e.g. with countries) that"
        u" are administered by your organisation",
        required=False,
    )

    organisational_contact_information = RichText(
        title=_(u"Contact information for the Observatory"),
        description=u"Please provide a corporate email or contact"
        u' form link into the "Default section", here you'
        u" may provide further contact information relevant"
        u" for the organisation's contribution to the"
        u" Observatory.",
        required=False,
    )

    # form.fieldset('default',
    #              label=u'Item Description',
    #         fields=['acronym', 'title', 'description', 'long_description',
    #                 'keywords', 'sectors', 'climate_impacts', 'elements',
    #                 ]
    #         )

    logo = NamedBlobImage(
        title=_(u"Logo"),
        description=_(
            u"Upload a representative picture or logo for the item."
            u" Recommended size: at least 360/180 px, aspect ratio 2x"
        ),
        required=False,
    )

    blocks = JSONField(
        title=_("Blocks"),
        description=_("The JSON representation of the object blocks."),
        schema=BLOCKS_SCHEMA,
        default={
            "873aee9d-23fd-4a8e-aa82-7e53e36142a7": {
            "@type": "title", 
            "copyrightIcon": "ri-copyright-line"
            }, 
            "e7e101d3-0a6a-4976-8b0a-ab7603c642a9": {
            "@type": "tabs_block", 
            "data": {
                "blocks": {
                "cce027cd-5299-4c9a-80cf-b7a482df420b": {
                    "@type": "tab", 
                    "blocks": {
                    "1d4d73b0-618c-4c8b-a46b-1a924f98f4ac": {
                        "@type": "slate"
                    }, 
                    "6c34c28b-61fc-4381-957c-9e90e03d414a": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "c5b73741-add2-4ae8-a725-7cd29f0d6761", 
                            "field": {
                            "id": "websites", 
                            "title": "Websites", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "0020812e-8306-403d-a7bb-2755eff143d4", 
                            "field": {
                            "id": "special_tags", 
                            "title": "Special tagging", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "1501d18c-8c37-47aa-8b80-62e586b25219", 
                            "field": {
                            "id": "relatedItems", 
                            "title": "Related Items", 
                            "widget": "relations"
                            }
                        }, 
                        {
                            "@id": "9a3e06db-50fa-4021-b42e-5447a954b99d", 
                            "field": {
                            "id": "comments", 
                            "title": "Comments", 
                            "widget": "textarea"
                            }
                        }
                        ], 
                        "variation": "default"
                    }
                    }, 
                    "blocks_layout": {
                    "items": [
                        "6c34c28b-61fc-4381-957c-9e90e03d414a", 
                        "1d4d73b0-618c-4c8b-a46b-1a924f98f4ac"
                    ]
                    }, 
                    "title": "Reference info"
                }, 
                "d3c6f26c-1614-4fa4-84b8-32fa1d991b80": {
                    "@type": "tab", 
                    "blocks": {
                    "8ebe1709-c8c1-44e0-9e43-f9bd50223656": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "20640dfc-2d34-4b9f-9c88-1e0815f92eb6", 
                            "field": {
                            "id": "geochars", 
                            "title": "Geographic characterisation", 
                            "widget": "textarea"
                            }
                        }
                        ], 
                        "variation": "default"
                    }, 
                    "c46aa30b-e9d7-4536-b0d2-f5ab4da99fbf": {
                        "@type": "slate"
                    }
                    }, 
                    "blocks_layout": {
                    "items": [
                        "8ebe1709-c8c1-44e0-9e43-f9bd50223656", 
                        "c46aa30b-e9d7-4536-b0d2-f5ab4da99fbf"
                    ]
                    }, 
                    "title": "Geographic info"
                }, 
                "e30dbfb7-7108-4df2-9b7e-3ea782f1839d": {
                    "@type": "tab", 
                    "blocks": {
                    "345db6db-1783-4bc2-a0e7-578b2d98e319": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "35151c19-79ba-48fc-b1c9-e9ac27bf666a", 
                            "field": {
                            "id": "publication_date", 
                            "title": "Date of item's creation", 
                            "widget": "date"
                            }
                        }, 
                        {
                            "@id": "c1a6479a-ee17-4ba5-a1cf-a1b5518bd194", 
                            "field": {
                            "id": "acronym", 
                            "title": "Acronym", 
                            "widget": "string"
                            }
                        }, 
                        {
                            "@id": "97fca98f-d401-4609-be06-75dc246565a5", 
                            "field": {
                            "id": "title", 
                            "title": "Name", 
                            "widget": "title"
                            }
                        }, 
                        {
                            "@id": "13584695-1b5d-46d2-93df-0ad0147f3824", 
                            "field": {
                            "id": "description", 
                            "title": "Short summary", 
                            "widget": "description"
                            }
                        }, 
                        {
                            "@id": "6c175970-4be3-4592-8e4c-17aed8477c96", 
                            "field": {
                            "id": "long_description", 
                            "title": "Description", 
                            "widget": "richtext"
                            }
                        }, 
                        {
                            "@id": "139c3d4d-d2d5-43c7-b923-4308ae2176db", 
                            "field": {
                            "id": "keywords", 
                            "title": "Keywords", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "9bf95e74-c573-4df4-a70f-6779cd2194fc", 
                            "field": {
                            "id": "sectors", 
                            "title": "Sectors", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "85e57766-dd24-46a8-a488-c256a01a8abd", 
                            "field": {
                            "id": "climate_impacts", 
                            "title": "Climate impacts", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "0906e2fe-00e4-476e-82d3-5b3ac3571a20", 
                            "field": {
                            "id": "elements", 
                            "title": "Adaptation elements", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "5224bb84-8f89-4bd1-be21-1e02bd3f0d02", 
                            "field": {
                            "id": "logo", 
                            "title": "Logo", 
                            "widget": "image"
                            }
                        }, 
                        {
                            "@id": "eed21c12-3400-4132-a814-c5205c9f50a9", 
                            "field": {
                            "id": "image", 
                            "title": "Thumbnail", 
                            "widget": "image"
                            }
                        }, 
                        {
                            "@id": "d572121f-aaff-43cd-b989-3d217fcf7921", 
                            "field": {
                            "id": "origin_website", 
                            "title": "Item from third parties", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "3ef3c28d-3669-4ff8-a337-0ef7b3597ac7", 
                            "field": {
                            "id": "contact", 
                            "title": "Contact", 
                            "widget": "string"
                            }
                        }
                        ], 
                        "variation": "default"
                    }, 
                    "c2913a3f-e4d1-481d-a086-f7f05ef39751": {
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
                    "blocks_layout": {
                    "items": [
                        "345db6db-1783-4bc2-a0e7-578b2d98e319", 
                        "c2913a3f-e4d1-481d-a086-f7f05ef39751"
                    ]
                    }, 
                    "title": "Item description"
                }, 
                "e72ad0f9-e9eb-473a-bf07-3e05d4a15135": {
                    "@type": "tab", 
                    "blocks": {
                    "c565b4f3-e11e-46ba-8a38-0faa1ca3d4b8": {
                        "@type": "slate"
                    }, 
                    "c6a2ec54-c105-4845-9190-2cc3e5bb31d8": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "1b240cfd-65ac-4020-85d3-90852f9cfed8", 
                            "field": {
                            "id": "include_in_observatory", 
                            "title": "Include in observatory", 
                            "widget": "boolean"
                            }
                        }, 
                        {
                            "@id": "7f60ebe8-bfbf-4da2-8a53-a617599774c3", 
                            "field": {
                            "id": "include_in_mission", 
                            "title": "Include in the Mission Portal", 
                            "widget": "boolean"
                            }
                        }
                        ], 
                        "variation": "default"
                    }
                    }, 
                    "blocks_layout": {
                    "items": [
                        "c6a2ec54-c105-4845-9190-2cc3e5bb31d8", 
                        "c565b4f3-e11e-46ba-8a38-0faa1ca3d4b8"
                    ]
                    }, 
                    "title": "Inclusion in subsites"
                }
                }, 
                "blocks_layout": {
                "items": [
                    "e30dbfb7-7108-4df2-9b7e-3ea782f1839d", 
                    "cce027cd-5299-4c9a-80cf-b7a482df420b", 
                    "d3c6f26c-1614-4fa4-84b8-32fa1d991b80", 
                    "e72ad0f9-e9eb-473a-bf07-3e05d4a15135"
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
                "873aee9d-23fd-4a8e-aa82-7e53e36142a7", 
                "e7e101d3-0a6a-4976-8b0a-ab7603c642a9"
            ]
        },
        required=False,
    )

alsoProvides(IOrganisation["acronym"], ILanguageIndependentField)
alsoProvides(IOrganisation["contact"], ILanguageIndependentField)
alsoProvides(IOrganisation["organisational_websites"], ILanguageIndependentField)
alsoProvides(IOrganisation["organisational_contact_information"], ILanguageIndependentField)
alsoProvides(IOrganisation["logo"], ILanguageIndependentField)
