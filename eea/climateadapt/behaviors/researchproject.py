from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.behaviors.aceitem import IAceItem
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField


class IResearchProject(IAceItem):
    """ResearchProject Interface"""

    blocks = JSONField(
        title=_("Blocks"),
        description=_("The JSON representation of the object blocks."),
        schema=BLOCKS_SCHEMA,
        default={
            "24bfc346-94c4-4b44-8c58-c4f72a2eb964": {
            "@type": "tabs_block", 
            "data": {
                "blocks": {
                "0c0b33a9-a7eb-4247-b891-98e033356f69": {
                    "@type": "tab", 
                    "blocks": {
                    "1e6a5735-1097-4fd0-b663-79ec34d474c2": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "c05b3cd8-b9b0-4a79-b11c-8b71f30f9101", 
                            "field": {
                            "id": "geochars", 
                            "title": "Geographic characterisation", 
                            "widget": "textarea"
                            }
                        }
                        ], 
                        "variation": "default"
                    }, 
                    "eefa935b-53db-49a0-80dd-8bf518abcf18": {
                        "@type": "slate"
                    }
                    }, 
                    "blocks_layout": {
                    "items": [
                        "1e6a5735-1097-4fd0-b663-79ec34d474c2", 
                        "eefa935b-53db-49a0-80dd-8bf518abcf18"
                    ]
                    }, 
                    "title": "Geographic info"
                }, 
                "2115ee00-bf5d-4398-b83a-84f55f67b730": {
                    "@type": "tab", 
                    "blocks": {
                    "6ced4b27-fa65-4627-926a-b2e6588265e6": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "f54c06a1-65e0-4ec0-aeb2-5a60b395b2e9", 
                            "field": {
                            "id": "publication_date", 
                            "title": "Date of item's creation", 
                            "widget": "date"
                            }
                        }, 
                        {
                            "@id": "4d491aa2-6a38-4bc9-9989-997369583019", 
                            "field": {
                            "id": "title", 
                            "title": "Title", 
                            "widget": "title"
                            }
                        }, 
                        {
                            "@id": "eeb4b6ca-ada5-47bd-88bd-a3960912e458", 
                            "field": {
                            "id": "description", 
                            "title": "Short summary", 
                            "widget": "description"
                            }
                        }, 
                        {
                            "@id": "5a4f7f60-9c9d-4ec0-8e95-ed49765c05a2", 
                            "field": {
                            "id": "long_description", 
                            "title": "Description", 
                            "widget": "richtext"
                            }
                        }, 
                        {
                            "@id": "f151d6be-20c1-4739-a0f2-c358dabc365e", 
                            "field": {
                            "id": "keywords", 
                            "title": "Keywords", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "31575864-3b67-47f1-8200-e5d09bb9d688", 
                            "field": {
                            "id": "sectors", 
                            "title": "Sectors", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "5cd169bb-60a1-411e-b552-6e7e378bf29b", 
                            "field": {
                            "id": "climate_impacts", 
                            "title": "Climate impacts", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "5450efc7-29a2-44ea-afd6-ecd1745b257b", 
                            "field": {
                            "id": "elements", 
                            "title": "Adaptation elements", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "2c452f75-5a5a-4f16-b9ba-ef4127c67f4e", 
                            "field": {
                            "id": "logo", 
                            "title": "Logo", 
                            "widget": "image"
                            }
                        }, 
                        {
                            "@id": "01132e31-15c4-44f3-9fdf-66a9cc087e60", 
                            "field": {
                            "id": "image", 
                            "title": "Thumbnail", 
                            "widget": "image"
                            }
                        }, 
                        {
                            "@id": "7627a4a6-6927-4569-a061-32c13915d1e2", 
                            "field": {
                            "id": "origin_website", 
                            "title": "Item from third parties", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "a656fef1-3bad-4d03-8ef4-87abfa8cd666", 
                            "field": {
                            "id": "contributor_list", 
                            "title": "Contributor(s)", 
                            "widget": "relations"
                            }
                        }, 
                        {
                            "@id": "5e9aecc6-3d0e-4088-b641-9ce30d5a67cd", 
                            "field": {
                            "id": "other_contributor", 
                            "title": "Other contributor(s)", 
                            "widget": "textarea"
                            }
                        }
                        ], 
                        "variation": "default"
                    }, 
                    "beb01a1b-68cc-4911-abbb-56ff5cbd54d5": {
                        "@type": "slate"
                    }
                    }, 
                    "blocks_layout": {
                    "items": [
                        "6ced4b27-fa65-4627-926a-b2e6588265e6", 
                        "beb01a1b-68cc-4911-abbb-56ff5cbd54d5"
                    ]
                    }, 
                    "title": "Item description"
                }, 
                "863e2919-3f3c-4d14-a1d7-a7aa9c67c005": {
                    "@type": "tab", 
                    "blocks": {
                    "2c494947-79f9-4dfe-b916-3049ddd909db": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "63ebbadb-950e-4652-a0d9-ab70d4fea1cb", 
                            "field": {
                            "id": "websites", 
                            "title": "Websites", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "3a5688d4-899b-4a37-9a9d-bb7d0fa53afc", 
                            "field": {
                            "id": "source", 
                            "title": "References", 
                            "widget": "richtext"
                            }
                        }, 
                        {
                            "@id": "b0861919-1acf-483f-a9f4-da5c7c9a21d2", 
                            "field": {
                            "id": "special_tags", 
                            "title": "Special tagging", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "e1cfd8e4-1a76-42cb-aab7-299f8b6ef4c1", 
                            "field": {
                            "id": "comments", 
                            "title": "Comments", 
                            "widget": "textarea"
                            }
                        }
                        ], 
                        "variation": "default"
                    }, 
                    "f6cd76ef-ce0b-4d95-bcc5-45d4ef5b104f": {
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
                        "2c494947-79f9-4dfe-b916-3049ddd909db", 
                        "f6cd76ef-ce0b-4d95-bcc5-45d4ef5b104f"
                    ]
                    }, 
                    "title": "Reference info"
                }, 
                "b6bff40e-3eaf-4782-af3e-d91d9c823f07": {
                    "@type": "tab", 
                    "blocks": {
                    "22b7793b-e74f-458e-9cae-de0b5f9dc8d0": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "fd8171ae-1582-4784-bf29-61d24b021497", 
                            "field": {
                            "id": "id", 
                            "title": "Short name", 
                            "widget": "string"
                            }
                        }
                        ], 
                        "variation": "default"
                    }, 
                    "23273133-eb8c-4131-93cc-06f218a5facc": {
                        "@type": "slate"
                    }
                    }, 
                    "blocks_layout": {
                    "items": [
                        "22b7793b-e74f-458e-9cae-de0b5f9dc8d0", 
                        "23273133-eb8c-4131-93cc-06f218a5facc"
                    ]
                    }, 
                    "title": "Settings"
                }, 
                "c2cb64c5-780b-47cc-ac87-7efcfb63623a": {
                    "@type": "tab", 
                    "blocks": {
                    "0496d4d7-61b2-4d81-a581-ceb0ec93dfc2": {
                        "@type": "metadataSection", 
                        "fields": [
                        {
                            "@id": "50b125d0-48e7-4a29-8939-b2c6eb665336", 
                            "field": {
                            "id": "include_in_observatory", 
                            "title": "Include in observatory", 
                            "widget": "boolean"
                            }
                        }, 
                        {
                            "@id": "cd570c10-39fe-44cb-8c7c-7790c8234866", 
                            "field": {
                            "id": "include_in_mission", 
                            "title": "Include in the Mission Portal", 
                            "widget": "boolean"
                            }
                        }, 
                        {
                            "@id": "2053539e-5df2-4438-bf85-2c20aa0e59cf", 
                            "field": {
                            "id": "health_impacts", 
                            "title": "Health impacts", 
                            "widget": "array"
                            }
                        }, 
                        {
                            "@id": "941b1ab8-539e-48cf-a867-35c26772646a", 
                            "field": {
                            "id": "relatedItems", 
                            "title": "Related Items", 
                            "widget": "relations"
                            }
                        }
                        ], 
                        "variation": "default"
                    }, 
                    "c23d72f2-df42-4c86-b4d2-eef84bf76392": {
                        "@type": "slate"
                    }
                    }, 
                    "blocks_layout": {
                    "items": [
                        "0496d4d7-61b2-4d81-a581-ceb0ec93dfc2", 
                        "c23d72f2-df42-4c86-b4d2-eef84bf76392"
                    ]
                    }, 
                    "title": "Inclusion in subsites"
                }
                }, 
                "blocks_layout": {
                "items": [
                    "2115ee00-bf5d-4398-b83a-84f55f67b730", 
                    "863e2919-3f3c-4d14-a1d7-a7aa9c67c005", 
                    "0c0b33a9-a7eb-4247-b891-98e033356f69", 
                    "c2cb64c5-780b-47cc-ac87-7efcfb63623a", 
                    "b6bff40e-3eaf-4782-af3e-d91d9c823f07"
                ]
                }
            }, 
            "template": "default", 
            "verticalAlign": "flex-start"
            }, 
            "41c49483-40d2-4c61-a9df-4972609c6c38": {
            "@type": "title", 
            "copyrightIcon": "ri-copyright-line"
            }, 
            "a804a94a-d173-497d-ac7d-b33c4433821d": {
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
                "41c49483-40d2-4c61-a9df-4972609c6c38", 
                "24bfc346-94c4-4b44-8c58-c4f72a2eb964", 
                 "a804a94a-d173-497d-ac7d-b33c4433821d"
            ]
        },
        required=False,
    )
