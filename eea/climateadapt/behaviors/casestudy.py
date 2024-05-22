from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.behaviors.acemeasure import IAceMeasure
from plone.app.contenttypes.interfaces import IImage
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.namedfile.field import NamedBlobImage
from z3c.form.interfaces import IAddForm, IEditForm
from z3c.relationfield.schema import RelationChoice, RelationList
from zope.interface import alsoProvides
from zope.schema import Choice, List, TextLine
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField

class ICaseStudy(IAceMeasure, IBlocks):  # , IGeolocatable):
    """Case study"""

    directives.omitted(IEditForm, "featured")
    directives.omitted(IAddForm, "featured")
    directives.omitted(IEditForm, "primephoto")
    directives.omitted(IAddForm, "primephoto")
    directives.omitted(IEditForm, "supphotos")
    directives.omitted(IAddForm, "supphotos")

    # directives.omitted(IEditForm, 'year')
    # directives.omitted(IAddForm, 'year')
    # directives.omitted(IEditForm, 'relatedItems')
    # directives.omitted(IAddForm, 'relatedItems')

    challenges = RichText(
        title=_(u"Challenges"),
        required=True,
        default=None,
        description=_(
            u"Describe what are the main climate change "
            u"impacts/risks and related challenges addressed by the "
            u"adaptation solutions proposed by the case study. "
            u"Possibly include quantitate scenarios/projections of "
            u"future climate change considered by the case study "
            u"(5,000 characters limit):"
        ),
    )

    objectives = RichText(
        title=_(u"Objectives"),
        required=True,
        default=None,
        description=_(
            u"Describe the objectives which triggered the "
            u"adaptation measures (5,000 characters limit):"
        ),
    )

    solutions = RichText(
        title=_(u"Solutions"),
        required=True,
        default=None,
        description=_(
            u"Describe the climate change adaptation solution(s) "
            u"implemented (5,000 characters limit):"
        ),
    )

    form.widget(relevance="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    relevance = List(
        title=_(u"Relevance"),
        required=True,
        missing_value=[],
        default=None,
        description=_(
            u"Select only one category below that best describes "
            u"how relevant this case study is to climate change "
            u"adaptation:"
        ),
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_relevance",
        ),
    )

    contact = RichText(
        title=_(u"Contact"),
        required=True,
        default=u"",
        description=_(
            u"Contact of reference (institution and persons) who is "
            u"directly involved in the development and "
            u"implementation of the case. (500 char limit) "
        ),
    )

    adaptationoptions = RelationList(
        title=u"Adaptation measures implemented in the case:",
        default=[],
        description=_(
            u"Select one or more adaptation options that this item " u"relates to:"
        ),
        value_type=RelationChoice(
            title=_(u"Related"),
            vocabulary="eea.climateadapt.adaptation_options"
            # source=ObjPathSourceBinder(),
            # source=CatalogSource(portal_type='eea.climateadapt.adaptionoption'),
        ),
        required=False,
    )

    primary_photo = NamedBlobImage(
        title=_(u"Primary photo"),
        required=False,
    )

    # dexteritytextindexer.searchable("source")
    source = RichText(
        title=_(u"References"),
        required=False,
        description=_(
            u"Describe the references (projects, a tools reports, etc.) "
            u"related to this item, providing further information about "
            u"it or its source."
        ),
    )

    primary_photo_copyright = TextLine(
        title=_(u"Primary Photo Copyright"),
        required=False,
        default=u"",
        description=_(
            u"Copyright statement or other rights information for  "
            u"the primary photo."
        ),
    )

    form.widget(elements="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    elements = List(
        title=_("Adaptation elements"),
        description=_("Select one or more elements."),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_elements_case_study",
        ),
    )

    # BBB fields, only used during migration
    primephoto = RelationChoice(
        title=_(u"Prime photo"),
        source=ObjPathSourceBinder(object_provides=IImage.__identifier__),
        required=False,
    )
    supphotos = RelationList(
        title=u"Gallery",
        default=[],
        value_type=RelationChoice(
            title=_(u"Related"),
            source=ObjPathSourceBinder(object_provides=IImage.__identifier__),
        ),
        required=False,
    )

    # form.fieldset(
    #     "default",
    #     label=u"Item Description",
    #     fields=[
    #         'title',
    #         'description',
    #         'long_description',
    #         'primary_photo',
    #         'primary_photo_copyright',
    #         'origin_website',
    #         'logo',
    #         'image',
    #         'contributor_list',
    #         'other_contributor',
    #         "climate_impacts",
    #         "challenges",
    #         "objectives",
    #         "adaptationoptions",
    #         "solutions",
    #         "relevance",
    #         "keywords",
    #         "sectors",
    #         "elements",
    #         # "featured",  # 'year',
    #     ],
    # )

    blocks = JSONField(
        title=_("Blocks"),
        description=_("The JSON representation of the object blocks."),
        schema=BLOCKS_SCHEMA,
        default={
            "3f1f3ddd-0c38-4408-9ab7-5191099dec50": {
            "@type": "title", 
            "copyrightIcon": "ri-copyright-line"
            }, 
            "d4ea2e59-b6ba-44e7-a720-06d31d9d3e5c": {
            "@type": "tabs_block", 
            "data": {
                "blocks": {
                "0b28077a-f698-4ca4-b932-48783a623519": {
                    "@type": "tab", 
                    "blocks": {
                    "e416be82-c5df-4acd-98e9-675dbb88298c": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "80e5975a-c12b-4f5c-8ce0-89706e2def32", 
                            "field": {
                            "id": "stakeholder_participation", 
                            "title": "Stakeholder participation", 
                            "widget": "richtext"
                            }
                        }, 
                        {
                            "@id": "ae0e8da3-2cd2-4395-908f-0af3e46a942d", 
                            "field": {
                            "id": "success_limitations", 
                            "title": "Success / limitations", 
                            "widget": "richtext"
                            }
                        }, 
                        {
                            "@id": "80286b54-736a-4ebc-b09a-71ddef8d8bd8", 
                            "field": {
                            "id": "cost_benefit", 
                            "title": "Cost / Benefit", 
                            "widget": "richtext"
                            }
                        }, 
                        {
                            "@id": "7a998946-1461-4aea-bf8e-65c19547e7fe", 
                            "field": {
                            "id": "legal_aspects", 
                            "title": "Legal aspects", 
                            "widget": "richtext"
                            }
                        }, 
                        {
                            "@id": "db32e80b-a32d-4af0-933e-1f56a2b21aec", 
                            "field": {
                            "id": "implementation_time", 
                            "title": "Implementation Time", 
                            "widget": "richtext"
                            }
                        }, 
                        {
                            "@id": "1d76bb7c-d417-40fd-b4bc-375c7c0d3248", 
                            "field": {
                            "id": "lifetime", 
                            "title": "Lifetime", 
                            "widget": "richtext"
                            }
                        }
                        ], 
                        "variation": "default"
                    }
                    }, 
                    "blocks_layout": {
                    "items": [
                        "e416be82-c5df-4acd-98e9-675dbb88298c"
                    ]
                    }, 
                    "title": "Additional details"
                }, 
                "43e34955-feb2-4c85-b3d0-f8afa4397b0a": {
                    "@type": "tab", 
                    "blocks": {
                    "852102b8-ef6e-44ee-a6b6-a55bd7321dc5": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "5ea6c91a-9ecc-4639-a5ad-39c777da271d", 
                            "field": {
                            "id": "governance_level", 
                            "title": "Governance Level", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "79b7f6a2-a8d8-4f09-b907-415f8d485799", 
                            "field": {
                            "id": "geochars", 
                            "title": "Geographic characterisation", 
                            "widget": "textarea"
                            }
                        }, 
                        {
                            "@id": "906faa69-0a7d-4fbf-a692-202a545db608", 
                            "field": {
                            "id": "geolocation", 
                            "title": "Geolocation", 
                            "widget": "file"
                            }
                        }
                        ], 
                        "variation": "default"
                    }
                    }, 
                    "blocks_layout": {
                    "items": [
                        "852102b8-ef6e-44ee-a6b6-a55bd7321dc5"
                    ]
                    }, 
                    "title": "Geographic info"
                }, 
                "8c14ec8c-3704-4381-a193-c3698459eb35": {
                    "@type": "tab", 
                    "blocks": {
                    "05b1558d-86ca-44ac-8f15-f150b0625aab": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "c3244293-23b9-4ab6-8524-f7a37e7a1644", 
                            "field": {
                            "id": "publication_date", 
                            "title": "Date of item's creation", 
                            "widget": "date"
                            }
                        }, 
                        {
                            "@id": "68c6e0e6-2e4d-4539-a8e6-ff22c5a137a2", 
                            "field": {
                            "id": "title", 
                            "title": "Title", 
                            "widget": "title"
                            }
                        }, 
                        {
                            "@id": "ecb9d2ee-3757-4d33-be2c-686152a3610a", 
                            "field": {
                            "id": "description", 
                            "title": "Short summary", 
                            "widget": "description"
                            }
                        }, 
                        {
                            "@id": "75aaed01-8e91-4bf7-bbdf-b133c3a222e9", 
                            "field": {
                            "id": "long_description", 
                            "title": "Description", 
                            "widget": "richtext"
                            }
                        }, 
                        {
                            "@id": "c591457f-1d18-4136-b506-5594ce81e549", 
                            "field": {
                            "id": "logo", 
                            "title": "Logo", 
                            "widget": "image"
                            }
                        }, 
                        {
                            "@id": "7ce74052-db09-4a0a-9812-a8b0cb7d6957", 
                            "field": {
                            "id": "primary_photo", 
                            "title": "Primary photo", 
                            "widget": "image"
                            }
                        }, 
                        {
                            "@id": "04449d0e-62ff-4778-a295-7b57ce1952a4", 
                            "field": {
                            "id": "primary_photo_copyright", 
                            "title": "Primary Photo Copyright", 
                            "widget": "string"
                            }
                        }, 
                        {
                            "@id": "ecfe707e-970c-490b-a942-97c1337e4095", 
                            "field": {
                            "id": "image", 
                            "title": "Thumbnail", 
                            "widget": "image"
                            }
                        }, 
                        {
                            "@id": "9a5b8507-6730-4762-bcd6-4fc1b10c7710", 
                            "field": {
                            "id": "climate_impacts", 
                            "title": "Climate impacts", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "6936482f-f3db-45b7-bb10-d2b8d69dcf32", 
                            "field": {
                            "id": "challenges", 
                            "title": "Challenges", 
                            "widget": "richtext"
                            }
                        }, 
                        {
                            "@id": "d903f345-1f5b-402a-8ca3-9d7108fe60af", 
                            "field": {
                            "id": "objectives", 
                            "title": "Objectives", 
                            "widget": "richtext"
                            }
                        }, 
                        {
                            "@id": "7bcac560-a25d-4845-b397-21d6e476e569", 
                            "field": {
                            "id": "adaptationoptions", 
                            "title": "Adaptation measures implemented in the case:", 
                            "widget": "relations"
                            }
                        }, 
                        {
                            "@id": "f51092ac-6986-4f07-9993-871f2111cad9", 
                            "field": {
                            "id": "solutions", 
                            "title": "Solutions", 
                            "widget": "richtext"
                            }
                        }, 
                        {
                            "@id": "c5480561-405a-4634-b925-bb31f1bef472", 
                            "field": {
                            "id": "relevance", 
                            "title": "Relevance", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "775a5368-df44-42b4-814e-02efb7f79d61", 
                            "field": {
                            "id": "keywords", 
                            "title": "Keywords", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "18953f8e-29bf-4868-94d6-5fccd2a759a7", 
                            "field": {
                            "id": "sectors", 
                            "title": "Sectors", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "ad026a59-e3e0-44a6-b809-46edead10a44", 
                            "field": {
                            "id": "elements", 
                            "title": "Adaptation elements", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "2aa73c72-2376-42fb-a216-83b2ed8d0def", 
                            "field": {
                            "id": "contributor_list", 
                            "title": "Contributor(s)", 
                            "widget": "relations"
                            }
                        }, 
                        {
                            "@id": "584150ff-adc0-4e0f-bb79-49d7b18863f5", 
                            "field": {
                            "id": "other_contributor", 
                            "title": "Other contributor(s)", 
                            "widget": "textarea"
                            }
                        }, 
                        {
                            "@id": "d36945e8-5efb-4932-a606-a7bf4d45d3ab", 
                            "field": {
                            "id": "origin_website", 
                            "title": "Item from third parties", 
                            "widget": "array"
                            }
                        }
                        ], 
                        "variation": "default"
                    }
                    }, 
                    "blocks_layout": {
                    "items": [
                        "05b1558d-86ca-44ac-8f15-f150b0625aab"
                    ]
                    }, 
                    "title": "Item description"
                }, 
                "c94564c7-2eae-4801-8f59-4e391ae6636c": {
                    "@type": "tab", 
                    "blocks": {
                    "d54abe78-0596-4650-a3af-73f3bd597b5f": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "b61d6bc3-a2a5-4372-a327-baeb5fe769d9", 
                            "field": {
                            "id": "include_in_observatory", 
                            "title": "Include in observatory", 
                            "widget": "boolean"
                            }
                        }, 
                        {
                            "@id": "95ebbd25-2e1a-4426-ba6c-de261f460a2d", 
                            "field": {
                            "id": "include_in_mission", 
                            "title": "Include in the Mission Portal", 
                            "widget": "boolean"
                            }
                        }, 
                        {
                            "@id": "97f90179-cb2e-4747-a878-f10e6464e0bf", 
                            "field": {
                            "id": "health_impacts", 
                            "title": "Health impacts", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "d52bf489-5c2c-447b-a8a6-955fd44c0c20", 
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
                        "d54abe78-0596-4650-a3af-73f3bd597b5f"
                    ]
                    }, 
                    "title": "Include in ECHO"
                }, 
                "def26b70-983a-4d51-8563-c0f3a54267de": {
                    "@type": "tab", 
                    "blocks": {
                    "3a2c0011-323a-4a95-9948-76ad7d7c61be": {
                        "@type": "slate"
                    }, 
                    "8045304a-9f8b-4946-bda4-b45bfd150aba": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "2e92b309-4967-4669-ab70-be4e10a1b52d", 
                            "field": {
                            "id": "contact", 
                            "title": "Contact", 
                            "widget": "richtext"
                            }
                        }, 
                        {
                            "@id": "5f61771b-2d7c-4a05-afaf-aa4d035b615f", 
                            "field": {
                            "id": "websites", 
                            "title": "Websites", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "2063c06d-90ed-404b-a0e5-b4cf1d778cf8", 
                            "field": {
                            "id": "source", 
                            "title": "References", 
                            "widget": "richtext"
                            }
                        }, 
                        {
                            "@id": "f4731661-9d0e-42d4-894e-997ed339d5c6", 
                            "field": {
                            "id": "special_tags", 
                            "title": "Special tagging", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "57e4fbdd-ab03-4fa7-a758-e9eb4add1d50", 
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
                        "8045304a-9f8b-4946-bda4-b45bfd150aba", 
                        "3a2c0011-323a-4a95-9948-76ad7d7c61be"
                    ]
                    }, 
                    "title": "Reference info"
                }
                }, 
                "blocks_layout": {
                "items": [
                    "8c14ec8c-3704-4381-a193-c3698459eb35", 
                    "0b28077a-f698-4ca4-b932-48783a623519", 
                    "def26b70-983a-4d51-8563-c0f3a54267de", 
                    "43e34955-feb2-4c85-b3d0-f8afa4397b0a", 
                    "c94564c7-2eae-4801-8f59-4e391ae6636c"
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
                "3f1f3ddd-0c38-4408-9ab7-5191099dec50", 
                "d4ea2e59-b6ba-44e7-a720-06d31d9d3e5c"
            ]
        },
        required=False,
    )


alsoProvides(ICaseStudy["relevance"], ILanguageIndependentField)
alsoProvides(ICaseStudy["contact"], ILanguageIndependentField)
alsoProvides(ICaseStudy["adaptationoptions"], ILanguageIndependentField)
alsoProvides(ICaseStudy["primary_photo"], ILanguageIndependentField)
alsoProvides(ICaseStudy["primary_photo_copyright"], ILanguageIndependentField)
alsoProvides(ICaseStudy["primephoto"], ILanguageIndependentField)
alsoProvides(ICaseStudy["supphotos"], ILanguageIndependentField)
