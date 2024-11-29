from plone.autoform import directives
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.textfield import RichText
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField
from z3c.relationfield.schema import RelationChoice, RelationList
from zope.interface import alsoProvides
from zope.schema import (
    Choice,
    Date,
    List,
)

from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.behaviors.acemeasure import IAceMeasure


class IAdaptationOption(IAceMeasure, IBlocks):
    """Adaptation Option"""

    # directives.omitted(IEditForm, 'featured')
    # directives.omitted(IAddForm, 'featured')

    # directives.omitted(IEditForm, 'year')
    # directives.omitted(IAddForm, 'year')

    directives.widget(
        key_type_measures="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    key_type_measures = List(
        title=_("Key Type Measures"),
        description=_("Select Key Type Measures. The options are:"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_key_type_measures",
        ),
    )

    directives.widget(ipcc_category="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    ipcc_category = List(
        title=_("IPCC adaptation options categories"),
        description=_(
            "Select one or more categories of adaptation options. " "The options are:"
        ),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_ipcc_category",
        ),
    )

    casestudies = RelationList(
        title=_("Case studies implemented in the adaption"),
        default=[],
        description=_(
            "Select one or more case study that this item " "relates to:"),
        value_type=RelationChoice(
            title=_("Related"),
            vocabulary="eea.climateadapt.case_studies",
            # source=ObjPathSourceBinder(),
            # source=CatalogSource(portal_type='eea.climateadapt.adaptionoption'),
        ),
        required=False,
    )

    publication_date = Date(
        title=_("Date of item's creation"),
        description=_(
            "The date refers to the moment in which the item "
            "has been prepared or  updated by contributing "
            "experts to be submitted for the publication in "
            "Climate ADAPT."
            " Please use the Calendar icon to add day/month/year. If you want to "
            'add only the year, please select "day: 1", "month: January" '
            "and then the year"
        ),
        required=True,
    )

    # dexteritytextindexer.searchable("source")
    source = RichText(
        title=_("References"),
        required=False,
        description=_(
            "Describe the references (projects, a tools reports, etc.) "
            "related to this item, providing further information about "
            "it or its source."
        ),
    )

    blocks = JSONField(
        title=_("Blocks"),
        description=_("The JSON representation of the object blocks."),
        schema=BLOCKS_SCHEMA,
        default={
            "1ec6dc0f-e15a-4c1f-827e-0152ab2cad6e": {"@type": "slate"},
            "a9dd800e-d56f-439a-9277-b82e7e0afd0f": {
                "@type": "tabs_block",
                "data": {
                    "blocks": {
                        "09a33128-3001-4ecb-a914-c91a800d9188": {
                            "@type": "tab",
                            "blocks": {
                                "9221b870-ab5b-4b22-a89d-014931abc8a3": {
                                    "@type": "metadataSection",
                                    "fields": [
                                        {
                                            "@id": "c0f27da8-b182-4568-803a-7b7e442138f7",
                                            "field": {
                                                "id": "websites",
                                                "title": "Websites",
                                                "widget": "array",
                                            },
                                        },
                                        {
                                            "@id": "372c5d3a-e969-4b5b-a52d-135c151c9ba9",
                                            "field": {
                                                "id": "source",
                                                "title": "References",
                                                "widget": "richtext",
                                            },
                                        },
                                        {
                                            "@id": "7d5e0c8f-ef66-4b5c-8213-006b1ef207db",
                                            "field": {
                                                "id": "special_tags",
                                                "title": "Special tagging",
                                                "widget": "array",
                                            },
                                        },
                                        {
                                            "@id": "150b2367-b4db-4b3c-943c-d25346715a3e",
                                            "field": {
                                                "id": "comments",
                                                "title": "Comments",
                                                "widget": "textarea",
                                            },
                                        },
                                        {
                                            "@id": "3d59e3e1-0b8b-4791-8432-fdcef7523ee1",
                                            "field": {
                                                "id": "relatedItems",
                                                "title": "Related Items",
                                                "widget": "relations",
                                            },
                                        },
                                    ],
                                    "variation": "default",
                                },
                                "f1a527a4-e9a0-4cb9-ba02-1f7d42e99814": {
                                    "@type": "slate"
                                },
                            },
                            "blocks_layout": {
                                "items": [
                                    "9221b870-ab5b-4b22-a89d-014931abc8a3",
                                    "f1a527a4-e9a0-4cb9-ba02-1f7d42e99814",
                                ]
                            },
                            "title": "Reference info",
                        },
                        "119d1efb-3753-4e1c-b6e8-122e6e514623": {
                            "@type": "tab",
                            "blocks": {
                                "70b4ba03-11f2-4eaa-8e05-ee3ebaa2d44d": {
                                    "@type": "slate"
                                },
                                "ea3e3896-f8e2-4bbf-b138-b6a512b1dc41": {
                                    "@type": "metadataSection",
                                    "fields": [
                                        {
                                            "@id": "7273a08b-ab74-4da2-94d6-5076a5419044",
                                            "field": {
                                                "id": "include_in_observatory",
                                                "title": "Include in observatory",
                                                "widget": "boolean",
                                            },
                                        },
                                        {
                                            "@id": "b0d7ad31-854b-492f-a9a3-3be356a21a7d",
                                            "field": {
                                                "id": "include_in_mission",
                                                "title": "Include in the Mission Portal",
                                                "widget": "boolean",
                                            },
                                        },
                                        {
                                            "@id": "0c08812e-0aaf-4f30-8687-3766e4526f5d",
                                            "field": {
                                                "id": "health_impacts",
                                                "title": "Health impacts",
                                                "widget": "array",
                                            },
                                        },
                                    ],
                                    "variation": "default",
                                },
                            },
                            "blocks_layout": {
                                "items": [
                                    "ea3e3896-f8e2-4bbf-b138-b6a512b1dc41",
                                    "70b4ba03-11f2-4eaa-8e05-ee3ebaa2d44d",
                                ]
                            },
                            "title": "Include in subsites",
                        },
                        "773065a4-7d83-4ba3-9c39-5799d0768881": {
                            "@type": "tab",
                            "blocks": {
                                "2f022310-0589-4cfe-a59f-43b8f579a4c4": {
                                    "@type": "slate"
                                },
                                "418c6ad5-c855-4b7d-927e-30506b0d924a": {
                                    "@type": "metadataSection",
                                    "fields": [
                                        {
                                            "@id": "e8005f85-b5f9-4fc3-a706-b1eb65799b22",
                                            "field": {
                                                "id": "governance_level",
                                                "title": "Governance Level",
                                                "widget": "array",
                                            },
                                        },
                                        {
                                            "@id": "2c6301d6-8ffd-4b65-bd6c-68cef7c6a1aa",
                                            "field": {
                                                "id": "geochars",
                                                "title": "Geographic characterisation",
                                                "widget": "textarea",
                                            },
                                        },
                                    ],
                                    "variation": "default",
                                },
                            },
                            "blocks_layout": {
                                "items": [
                                    "418c6ad5-c855-4b7d-927e-30506b0d924a",
                                    "2f022310-0589-4cfe-a59f-43b8f579a4c4",
                                ]
                            },
                            "title": "Geographic info",
                        },
                        "b2fecfe1-3cea-4959-a127-416128ba10ad": {
                            "@type": "tab",
                            "blocks": {
                                "7b9f67b6-13a5-4708-8b0c-fbd49cd30ce8": {
                                    "@type": "metadataSection",
                                    "fields": [
                                        {
                                            "@id": "9838df27-ec45-41a9-aff4-be005ac8d3f4",
                                            "field": {
                                                "id": "key_type_measures",
                                                "title": "Key Type Measures",
                                                "widget": "array",
                                            },
                                        },
                                        {
                                            "@id": "ff0d0ad2-7d2e-4830-9840-9119fe934a8e",
                                            "field": {
                                                "id": "ipcc_category",
                                                "title": "IPCC adaptation options categories",
                                                "widget": "array",
                                            },
                                        },
                                        {
                                            "@id": "debcb266-3968-4814-8f1b-2b6462c65985",
                                            "field": {
                                                "id": "stakeholder_participation",
                                                "title": "Stakeholder participation",
                                                "widget": "richtext",
                                            },
                                        },
                                        {
                                            "@id": "8b66f602-4098-4083-ae4e-0d45a6061c41",
                                            "field": {
                                                "id": "success_limitations",
                                                "title": "Success and limiting factors",
                                                "widget": "richtext",
                                            },
                                        },
                                        {
                                            "@id": "07bf6b42-bdef-4505-8a80-369d4f096d34",
                                            "field": {
                                                "id": "cost_benefit",
                                                "title": "Costs and benefits",
                                                "widget": "richtext",
                                            },
                                        },
                                        {
                                            "@id": "81ad38c7-b2db-432f-a598-ea34971fe8e3",
                                            "field": {
                                                "id": "legal_aspects",
                                                "title": "Legal aspects",
                                                "widget": "richtext",
                                            },
                                        },
                                        {
                                            "@id": "6f100215-d407-4049-be3e-8c15c45f48b9",
                                            "field": {
                                                "id": "implementation_time",
                                                "title": "Implementation time",
                                                "widget": "richtext",
                                            },
                                        },
                                        {
                                            "@id": "bbb2a138-3cbd-41c2-9894-07cb865ced37",
                                            "field": {
                                                "id": "lifetime",
                                                "title": "Lifetime",
                                                "widget": "richtext",
                                            },
                                        },
                                    ],
                                    "variation": "default",
                                },
                                "fe9aa724-a260-441d-bb1c-8d8cb31da996": {
                                    "@type": "slate"
                                },
                            },
                            "blocks_layout": {
                                "items": [
                                    "7b9f67b6-13a5-4708-8b0c-fbd49cd30ce8",
                                    "fe9aa724-a260-441d-bb1c-8d8cb31da996",
                                ]
                            },
                            "title": "Additional details",
                        },
                        "c8ddbedf-77f7-413d-8cf5-c9c93424b8b2": {
                            "@type": "tab",
                            "blocks": {
                                "cd9f90ca-a550-4ac2-912c-5f19a59fc7aa": {
                                    "@type": "slate"
                                },
                                "db21ff44-33a0-498d-a91c-a686cd388fcf": {
                                    "@type": "metadataSection",
                                    "fields": [
                                        {
                                            "@id": "abeb092c-8e96-40e2-85f4-dbb89edfa266",
                                            "field": {
                                                "id": "publication_date",
                                                "title": "Date of item's creation",
                                                "widget": "date",
                                            },
                                        },
                                        {
                                            "@id": "75b2b533-1191-4667-b688-5e05faa878a7",
                                            "field": {
                                                "id": "title",
                                                "title": "Title",
                                                "widget": "title",
                                            },
                                        },
                                        {
                                            "@id": "034e0740-1b69-4a79-987c-e7dcd7924617",
                                            "field": {
                                                "id": "description",
                                                "title": "Short summary",
                                                "widget": "description",
                                            },
                                        },
                                        {
                                            "@id": "05481433-be21-4aab-a91b-294786f66b8e",
                                            "field": {
                                                "id": "long_description",
                                                "title": "Description",
                                                "widget": "richtext",
                                            },
                                        },
                                        {
                                            "@id": "ac2653f1-007b-44f6-90e7-b01bb5a1be6e",
                                            "field": {
                                                "id": "climate_impacts",
                                                "title": "Climate impacts",
                                                "widget": "array",
                                            },
                                        },
                                        {
                                            "@id": "70bd7425-9803-4e70-9234-cb2976e0dbb9",
                                            "field": {
                                                "id": "keywords",
                                                "title": "Keywords",
                                                "widget": "array",
                                            },
                                        },
                                        {
                                            "@id": "120d3476-7753-40c6-a921-d5c7afed7b58",
                                            "field": {
                                                "id": "sectors",
                                                "title": "Sectors",
                                                "widget": "array",
                                            },
                                        },
                                        {
                                            "@id": "f93bbfbd-731b-4db9-8909-07d21d23c583",
                                            "field": {
                                                "id": "casestudies",
                                                "title": "Case studies implemented in the adaption",
                                                "widget": "relations",
                                            },
                                        },
                                        {
                                            "@id": "9ca3ab6b-6429-40fc-98ed-27b8292647a5",
                                            "field": {
                                                "id": "elements",
                                                "title": "Adaptation elements",
                                                "widget": "array",
                                            },
                                        },
                                        {
                                            "@id": "cbe3f50d-61a5-4705-abb3-76d301461ca9",
                                            "field": {
                                                "id": "logo",
                                                "title": "Logo",
                                                "widget": "image",
                                            },
                                        },
                                        {
                                            "@id": "5365f9ad-115f-4966-8c6e-8b033a0f735d",
                                            "field": {
                                                "id": "image",
                                                "title": "Thumbnail",
                                                "widget": "image",
                                            },
                                        },
                                        {
                                            "@id": "153dc9d3-f1dd-495e-b51a-a3a88c984f21",
                                            "field": {
                                                "id": "origin_website",
                                                "title": "Item from third parties",
                                                "widget": "array",
                                            },
                                        },
                                        {
                                            "@id": "944ebfac-7f35-4e66-8f3e-456f6d33cf7c",
                                            "field": {
                                                "id": "contributor_list",
                                                "title": "Contributor(s)",
                                                "widget": "relations",
                                            },
                                        },
                                        {
                                            "@id": "3cf77fde-27e3-495a-a6cc-a00e485bbac3",
                                            "field": {
                                                "id": "other_contributor",
                                                "title": "Other contributor(s)",
                                                "widget": "textarea",
                                            },
                                        },
                                        {"@id": "1ed89d52-1475-4590-bcfb-645442f01acc"},
                                    ],
                                    "variation": "default",
                                },
                            },
                            "blocks_layout": {
                                "items": [
                                    "db21ff44-33a0-498d-a91c-a686cd388fcf",
                                    "cd9f90ca-a550-4ac2-912c-5f19a59fc7aa",
                                ]
                            },
                            "title": "Item description",
                        },
                    },
                    "blocks_layout": {
                        "items": [
                            "c8ddbedf-77f7-413d-8cf5-c9c93424b8b2",
                            "b2fecfe1-3cea-4959-a127-416128ba10ad",
                            "09a33128-3001-4ecb-a914-c91a800d9188",
                            "773065a4-7d83-4ba3-9c39-5799d0768881",
                            "119d1efb-3753-4e1c-b6e8-122e6e514623",
                        ]
                    },
                },
                "template": "default",
                "verticalAlign": "flex-start",
            },
            "ec2dd403-0964-413c-ac37-67c2bbc0a4c9": {
                "@type": "title",
                "copyrightIcon": "ri-copyright-line",
            },
        },
        required=False,
    )

    blocks_layout = JSONField(
        title=_("Blocks Layout"),
        description=_("The JSON representation of the object blocks layout."),
        schema=LAYOUT_SCHEMA,
        default={
            "items": [
                "ec2dd403-0964-413c-ac37-67c2bbc0a4c9",
                "a9dd800e-d56f-439a-9277-b82e7e0afd0f",
                "1ec6dc0f-e15a-4c1f-827e-0152ab2cad6e",
            ]
        },
        required=False,
    )


alsoProvides(IAdaptationOption["publication_date"], ILanguageIndependentField)
alsoProvides(IAdaptationOption["casestudies"], ILanguageIndependentField)
alsoProvides(IAdaptationOption["ipcc_category"], ILanguageIndependentField)
alsoProvides(IAdaptationOption["key_type_measures"], ILanguageIndependentField)
