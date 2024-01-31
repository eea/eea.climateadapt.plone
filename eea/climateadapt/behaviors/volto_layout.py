indicator_layout_items = [
    "b0fb074f-9ef6-40b6-b7c8-a5c16df31cb7",
    "7bbd49e4-bfcb-46cf-bfd6-2db8749f7a11",
    "44fccbd7-da2f-4fd6-b565-3e7804dd8d52",
]
indicator_layout_blocks = {
    "44fccbd7-da2f-4fd6-b565-3e7804dd8d52": {
        "@type": "slate",
        "plaintext": "",
        "value": [{"children": [{"text": ""}], "type": "p"}],
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
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "cf28a9a5-c227-4393-a4eb-c8c0ca7c53b9",
                                    "field": {
                                        "id": "source",
                                        "title": "References",
                                        "widget": "richtext",
                                    },
                                },
                                {
                                    "@id": "dc6d7712-7baf-46c6-96c7-5fc69f9c0ec3",
                                    "field": {
                                        "id": "special_tags",
                                        "title": "Special tagging",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "f1872728-e4f4-4a27-bb0b-4098d520cb43",
                                    "field": {
                                        "id": "comments",
                                        "title": "Comments",
                                        "widget": "textarea",
                                    },
                                },
                                {
                                    "@id": "2d319998-75df-4072-a486-3c1761c53b03",
                                    "field": {
                                        "id": "relatedItems",
                                        "title": "Related Items",
                                        "widget": "relations",
                                    },
                                },
                            ],
                            "variation": "default",
                        },
                        "c284e0a6-6999-44d1-98e0-971ccdd7f350": {"@type": "slate"},
                    },
                    "blocks_layout": {
                        "items": [
                            "798778c7-e081-42c7-bf5f-08584e3034d5",
                            "c284e0a6-6999-44d1-98e0-971ccdd7f350",
                        ]
                    },
                    "title": "Reference Info",
                },
                "28dc71d9-a6c6-4bcd-8014-f29734f1570a": {
                    "@type": "tab",
                    "blocks": {
                        "8020320f-0c8a-43bb-bf05-1ef8411c7a3a": {"@type": "slate"},
                        "8d25d358-6d84-4d48-8ba7-bace0ddb98e7": {
                            "@type": "metadataSection",
                            "fields": [
                                {
                                    "@id": "9b4329d1-7f8e-4537-a63d-276ea5dd35e2",
                                    "field": {
                                        "id": "geochars",
                                        "title": "Geographic characterisation",
                                        "widget": "textarea",
                                    },
                                }
                            ],
                            "variation": "default",
                        },
                    },
                    "blocks_layout": {
                        "items": [
                            "8d25d358-6d84-4d48-8ba7-bace0ddb98e7",
                            "8020320f-0c8a-43bb-bf05-1ef8411c7a3a",
                        ]
                    },
                    "title": "Geographic Info",
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
                                        "widget": "datetime",
                                    },
                                },
                                {
                                    "@id": "f29ef125-91de-4cdd-953e-8b3d61880dfe",
                                    "field": {
                                        "id": "expires",
                                        "title": "Expiration Date",
                                        "widget": "datetime",
                                    },
                                },
                            ],
                            "variation": "default",
                        },
                        "6dd89747-194f-4d36-b40a-1ea96cda1136": {"@type": "slate"},
                    },
                    "blocks_layout": {
                        "items": [
                            "3c143313-5e3c-4b9f-a503-ebea07629392",
                            "6dd89747-194f-4d36-b40a-1ea96cda1136",
                        ]
                    },
                    "title": "Dates",
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
                                        "widget": "boolean",
                                    },
                                },
                                {
                                    "@id": "8c611ecf-10d1-4d60-ad9b-2896150e4b0d",
                                    "field": {
                                        "id": "include_in_observatory",
                                        "title": "Include in observatory",
                                        "widget": "boolean",
                                    },
                                },
                                {
                                    "@id": "94fddc95-7a32-4f4d-bb63-60ddcb76cf95",
                                    "field": {
                                        "id": "health_impacts",
                                        "title": "Health impacts",
                                        "widget": "array",
                                    },
                                },
                            ],
                            "variation": "default",
                        },
                        "9fb96674-da82-4dfb-9d4d-0d5cb817044d": {"@type": "slate"},
                    },
                    "blocks_layout": {
                        "items": [
                            "3d0c3e80-e2f0-42a3-88dd-358602a875d5",
                            "9fb96674-da82-4dfb-9d4d-0d5cb817044d",
                        ]
                    },
                    "title": "Inclusion in the subsites",
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
                                        "widget": "date",
                                    },
                                },
                                {
                                    "@id": "99979251-95f1-49bc-a315-172cf3d5f1f3",
                                    "field": {
                                        "id": "title",
                                        "title": "Title",
                                        "widget": "title",
                                    },
                                },
                                {
                                    "@id": "9456d8f2-23c7-49eb-b219-f3a0b64eb969",
                                    "field": {
                                        "id": "description",
                                        "title": "Short summary",
                                        "widget": "description",
                                    },
                                },
                                {
                                    "@id": "1c3acc04-e206-474e-ac80-fa3cb644fc92",
                                    "field": {
                                        "id": "long_description",
                                        "title": "Description",
                                        "widget": "richtext",
                                    },
                                },
                                {
                                    "@id": "f6be7cd4-a8fa-4392-80d2-b73e6412cf67",
                                    "field": {
                                        "id": "keywords",
                                        "title": "Keywords",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "e9b6b1f1-198f-4f10-85fb-0ad21af4c714",
                                    "field": {
                                        "id": "sectors",
                                        "title": "Sectors",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "d960fac3-c6e7-4f46-b08f-caca069faadb",
                                    "field": {
                                        "id": "climate_impacts",
                                        "title": "Climate impacts",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "425ae05c-c6d6-4fbc-8f1d-da26959fdc41",
                                    "field": {
                                        "id": "elements",
                                        "title": "Adaptation elements",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "7c085bd7-936b-41ad-ade6-8979d359c2e3",
                                    "field": {
                                        "id": "map_graphs",
                                        "title": "Map/Graphs",
                                        "widget": "textarea",
                                    },
                                },
                                {
                                    "@id": "c0dbddd0-c93f-457f-ad86-f3c667f1edc3",
                                    "field": {
                                        "id": "origin_website",
                                        "title": "Item from third parties",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "f360f89d-0958-485a-b49b-dc951e58bc34",
                                    "field": {
                                        "id": "logo",
                                        "title": "Logo",
                                        "widget": "image",
                                    },
                                },
                                {
                                    "@id": "5aa26ee2-21a8-41fe-8e25-b50df5a4c257",
                                    "field": {
                                        "id": "image",
                                        "title": "Thumbnail",
                                        "widget": "image",
                                    },
                                },
                                {
                                    "@id": "f14044da-c980-470f-934f-c7f487802a94",
                                    "field": {
                                        "id": "contributor_list",
                                        "title": "Contributor(s)",
                                        "widget": "relations",
                                    },
                                },
                                {
                                    "@id": "b76b541b-0f79-4802-85fc-5806adc78f84",
                                    "field": {
                                        "id": "other_contributor",
                                        "title": "Other contributor(s)",
                                        "widget": "textarea",
                                    },
                                },
                            ],
                            "variation": "default",
                        },
                        "a3738650-0a77-4d1d-9488-dacbfcc218f7": {"@type": "slate"},
                    },
                    "blocks_layout": {
                        "items": [
                            "3c2ebb66-f4cf-4228-b1c7-6617e2a49b24",
                            "a3738650-0a77-4d1d-9488-dacbfcc218f7",
                        ]
                    },
                    "title": "Item Description",
                },
            },
            "blocks_layout": {
                "items": [
                    "d6ef68a8-f7d9-4e1b-bece-58c499a9055d",
                    "25e5959e-f4b8-4a46-b523-56027296968c",
                    "28dc71d9-a6c6-4bcd-8014-f29734f1570a",
                    "c3449856-0cbe-497e-bdec-2ba9b191eaec",
                    "66d0290e-9862-489e-b0ab-ffcbdc858782",
                ]
            },
        },
        "template": "default",
        "verticalAlign": "flex-start",
    },
    "b0fb074f-9ef6-40b6-b7c8-a5c16df31cb7": {
        "@type": "title",
        "copyrightIcon": "ri-copyright-line",
    },
}

video_layout_blocks = {
    "2fd06a1a-25dc-49fc-a032-e377a676806b": {
        "@type": "title",
        "copyrightIcon": "ri-copyright-line",
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
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "bc7d44e1-cf49-41ee-a438-93aaa61eb3dd",
                                    "field": {
                                        "id": "source",
                                        "title": "References",
                                        "widget": "richtext",
                                    },
                                },
                                {
                                    "@id": "23714626-92a6-41eb-aaa1-8dd8e8da41c7",
                                    "field": {
                                        "id": "special_tags",
                                        "title": "Special tagging",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "4ca824d2-25c9-493a-96a7-808437814247",
                                    "field": {
                                        "id": "comments",
                                        "title": "Comments",
                                        "widget": "textarea",
                                    },
                                },
                            ],
                            "variation": "default",
                        },
                        "a92e340f-959f-4b35-ba5d-c91fed183148": {"@type": "slate"},
                    },
                    "blocks_layout": {
                        "items": [
                            "9b9f5a2c-b9b2-4156-a8dd-d041e3764ac3",
                            "a92e340f-959f-4b35-ba5d-c91fed183148",
                        ]
                    },
                    "title": "Reference info",
                },
                "87dcd7a3-02be-46aa-80fc-60296cff1d4f": {
                    "@type": "tab",
                    "blocks": {
                        "b0e83fc5-62d7-492e-8158-c34d65f04d37": {"@type": "slate"},
                        "b75ec765-8c1e-4a55-82eb-59762a4477be": {
                            "@type": "metadataSection",
                            "fields": [
                                {
                                    "@id": "a0226dc9-5232-4f7f-82fe-86be53ed99f0",
                                    "field": {
                                        "id": "geochars",
                                        "title": "Geographic characterisation",
                                        "widget": "textarea",
                                    },
                                }
                            ],
                            "variation": "default",
                        },
                    },
                    "blocks_layout": {
                        "items": [
                            "b75ec765-8c1e-4a55-82eb-59762a4477be",
                            "b0e83fc5-62d7-492e-8158-c34d65f04d37",
                        ]
                    },
                    "title": "Geographic info",
                },
                "979a324c-624b-43dc-84ab-31d7084de67a": {
                    "@type": "tab",
                    "blocks": {
                        "0a83446f-d0d9-41ab-8884-5a5e7dc41b12": {"@type": "slate"},
                        "667ff441-5cec-4d61-a7b0-c0230cbe67c8": {
                            "@type": "metadataSection",
                            "fields": [
                                {
                                    "@id": "c6720af7-0e89-4b07-a0b5-aaad1d49acc6",
                                    "field": {
                                        "id": "include_in_observatory",
                                        "title": "Include in observatory",
                                        "widget": "boolean",
                                    },
                                },
                                {
                                    "@id": "e6e419f8-31b3-4738-b1ff-8958f663a107",
                                    "field": {
                                        "id": "include_in_mission",
                                        "title": "Include in the Mission Portal",
                                        "widget": "boolean",
                                    },
                                },
                                {
                                    "@id": "c0c5a8d9-a06e-4fb5-ab3f-c6facd60e77d",
                                    "field": {
                                        "id": "health_impacts",
                                        "title": "Health impacts",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "6240962b-7933-44bc-8a05-762286a43755",
                                    "field": {
                                        "id": "relatedItems",
                                        "title": "Related Items",
                                        "widget": "relations",
                                    },
                                    "hideInView": False,
                                },
                            ],
                            "variation": "default",
                        },
                    },
                    "blocks_layout": {
                        "items": [
                            "667ff441-5cec-4d61-a7b0-c0230cbe67c8",
                            "0a83446f-d0d9-41ab-8884-5a5e7dc41b12",
                        ]
                    },
                    "title": "Inclusion in subsites",
                },
                "9c9c24e8-1f8c-4f11-9e44-a5c4769beb6d": {
                    "@type": "tab",
                    "blocks": {
                        "3191a23f-1835-4ffd-98ce-8e38f10c8901": {"@type": "slate"},
                        "319a868c-d713-40a8-963b-288c82e3397f": {
                            "@type": "metadataSection",
                            "fields": [
                                {
                                    "@id": "a49581e1-6772-4846-b68a-66d529fb8716",
                                    "field": {
                                        "id": "id",
                                        "title": "Short name",
                                        "widget": "string",
                                    },
                                }
                            ],
                            "variation": "default",
                        },
                    },
                    "blocks_layout": {
                        "items": [
                            "319a868c-d713-40a8-963b-288c82e3397f",
                            "3191a23f-1835-4ffd-98ce-8e38f10c8901",
                        ]
                    },
                    "title": "Settings",
                },
                "fd91f1d7-3499-4473-bd12-646a9129503b": {
                    "@type": "tab",
                    "blocks": {
                        "1ee28778-69d8-4e7f-944a-8efdf702b12a": {"@type": "slate"},
                        "6d1306eb-fb93-4e84-9c58-14636394851e": {
                            "@type": "metadataSection",
                            "fields": [
                                {
                                    "@id": "758e962f-acf1-46d4-b003-a8d8855efb67",
                                    "field": {
                                        "id": "publication_date",
                                        "title": "Date of video's release",
                                        "widget": "date",
                                    },
                                },
                                {
                                    "@id": "46d570fd-98bf-4341-92c8-7edf2b24bc15",
                                    "field": {
                                        "id": "video_height",
                                        "title": "Video Height",
                                        "widget": "string",
                                    },
                                },
                                {
                                    "@id": "de478a87-1560-4657-ada5-bc5cc03f71ee",
                                    "field": {
                                        "id": "embed_url",
                                        "title": "Video URL",
                                        "widget": "string",
                                    },
                                },
                                {
                                    "@id": "9745a47e-697a-4f44-b66b-1739c5ea3941",
                                    "field": {
                                        "id": "title",
                                        "title": "Title",
                                        "widget": "title",
                                    },
                                },
                                {
                                    "@id": "d644afa3-38d9-4d2b-97cb-3ccdec374c4a",
                                    "field": {
                                        "id": "description",
                                        "title": "Short summary",
                                        "widget": "description",
                                    },
                                },
                                {
                                    "@id": "452cd1ea-2cea-4f50-8f2f-1c3631df54cb",
                                    "field": {
                                        "id": "long_description",
                                        "title": "Description",
                                        "widget": "richtext",
                                    },
                                },
                                {
                                    "@id": "7984b59a-83f9-4c5b-a78c-ed551e9d00fc",
                                    "field": {
                                        "id": "keywords",
                                        "title": "Keywords",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "ad014d41-5315-4222-a085-bd3a3c70ed43",
                                    "field": {
                                        "id": "sectors",
                                        "title": "Sectors",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "cbefd4d3-22ca-4021-9812-52b4af844754",
                                    "field": {
                                        "id": "climate_impacts",
                                        "title": "Climate impacts",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "39b01189-4de8-4b84-ad63-170714d136f6",
                                    "field": {
                                        "id": "elements",
                                        "title": "Adaptation elements",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "da17b7b4-01b9-4098-84ac-c3b69124514b",
                                    "field": {
                                        "id": "logo",
                                        "title": "Logo",
                                        "widget": "image",
                                    },
                                },
                                {
                                    "@id": "023c96b1-e3d9-43d8-9416-f72e4d4ec03e",
                                    "field": {
                                        "id": "image",
                                        "title": "Thumbnail",
                                        "widget": "image",
                                    },
                                },
                                {
                                    "@id": "2d39bd5c-69b7-49ff-9829-7d6ec50bf002",
                                    "field": {
                                        "id": "origin_website",
                                        "title": "Item from third parties",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "79a785ca-68c5-413c-bb38-466555bdb451",
                                    "field": {
                                        "id": "contributor_list",
                                        "title": "Contributor(s)",
                                        "widget": "relations",
                                    },
                                },
                                {
                                    "@id": "909c32e9-ac82-496b-9c1b-5c79e9a25db9",
                                    "field": {
                                        "id": "other_contributor",
                                        "title": "Other contributor(s)",
                                        "widget": "textarea",
                                    },
                                },
                                {
                                    "@id": "67f9a021-fdc7-469b-953f-0e483a692323",
                                    "field": {
                                        "id": "related_documents_presentations",
                                        "title": "Related documents and presentations",
                                        "widget": "richtext",
                                    },
                                },
                            ],
                            "variation": "default",
                        },
                    },
                    "blocks_layout": {
                        "items": [
                            "6d1306eb-fb93-4e84-9c58-14636394851e",
                            "1ee28778-69d8-4e7f-944a-8efdf702b12a",
                        ]
                    },
                    "title": "Item description",
                },
            },
            "blocks_layout": {
                "items": [
                    "fd91f1d7-3499-4473-bd12-646a9129503b",
                    "01f426db-0c8f-460a-82db-daf84b6d2ec5",
                    "87dcd7a3-02be-46aa-80fc-60296cff1d4f",
                    "979a324c-624b-43dc-84ab-31d7084de67a",
                    "9c9c24e8-1f8c-4f11-9e44-a5c4769beb6d",
                ]
            },
        },
        "template": "default",
        "verticalAlign": "flex-start",
    },
    "99df1833-612c-42c8-b847-facf75786c44": {
        "@type": "slate",
        "plaintext": "",
        "value": [{"children": [{"text": ""}], "type": "p"}],
    },
}

video_layout_items = [
    "2fd06a1a-25dc-49fc-a032-e377a676806b",
    "5c1c7869-b4bd-4de6-ac89-8f145846c929",
    "99df1833-612c-42c8-b847-facf75786c44",
]

cca_event_blocks = {
    "1d17872f-06a8-4460-809c-ab14435bafe0": {
        "@type": "title",
        "copyrightIcon": "ri-copyright-line",
    },
    "392b0b2b-85c5-4d36-9c61-262d759b7562": {
        "@type": "slate",
        "plaintext": "",
        "value": [{"children": [{"text": ""}], "type": "p"}],
    },
    "8c106f0d-0928-444b-b016-5dd78a2e0eab": {
        "@type": "tabs_block",
        "data": {
            "blocks": {
                "11dbdd53-8d3c-43ec-b04e-b88f4adfe418": {
                    "@type": "tab",
                    "blocks": {
                        "6e994da1-12f3-40df-a92c-f5a26b538d16": {"@type": "slate"},
                        "b03fb0aa-19e4-4bbf-8932-559f0fb22bc3": {
                            "@type": "metadataSection",
                            "fields": [
                                {
                                    "@id": "79063149-0f86-4a38-964f-e47c11235e44",
                                    "field": {
                                        "id": "image",
                                        "title": "Thumbnail",
                                        "widget": "image",
                                    },
                                },
                                {
                                    "@id": "4c73d358-bdb8-4e3f-bd62-f6e20e74a2c5",
                                    "field": {
                                        "id": "subtitle",
                                        "title": "Subtitle",
                                        "widget": "string",
                                    },
                                },
                                {
                                    "@id": "672f0bb5-be52-499c-818c-e272b7663de6",
                                    "field": {
                                        "id": "online_event_url",
                                        "title": "More information on the event (URL)",
                                        "widget": "string",
                                    },
                                },
                                {
                                    "@id": "34b9f17b-ea0b-4204-8f49-d95e3dba572e",
                                    "field": {
                                        "id": "agenda_file",
                                        "title": "Agenda document",
                                        "widget": "file",
                                    },
                                },
                                {
                                    "@id": "fd69fb36-4ee2-4b09-a8d5-4c90e2916e42",
                                    "field": {
                                        "id": "agenda",
                                        "title": "Agenda",
                                        "widget": "richtext",
                                    },
                                },
                                {
                                    "@id": "94cab738-34fc-4a97-9174-84dec751260c",
                                    "field": {
                                        "id": "background_documents",
                                        "title": "Background documents",
                                        "widget": "file",
                                    },
                                },
                                {
                                    "@id": "f32dbee4-5769-468d-a94c-1a6378a638d3",
                                    "field": {
                                        "id": "participation",
                                        "title": "Participation",
                                        "widget": "richtext",
                                    },
                                },
                                {
                                    "@id": "35013a7e-5baa-413e-b483-db45f318789e",
                                    "field": {
                                        "id": "event_language",
                                        "title": "Event Language",
                                        "widget": "choices",
                                    },
                                },
                                {
                                    "@id": "471d9536-bec9-4485-a027-b5e9e1abb29c",
                                    "field": {
                                        "id": "online_registration",
                                        "title": "Online registration (URL)",
                                        "widget": "string",
                                    },
                                },
                                {
                                    "@id": "e3b02ccc-f858-4fb8-a624-dfdf841f8243",
                                    "field": {
                                        "id": "online_registration_message",
                                        "title": "Online registration message",
                                        "widget": "richtext",
                                    },
                                },
                                {
                                    "@id": "91744038-87cd-4910-9efa-da3c0fe895cc",
                                    "field": {
                                        "id": "online_registration_documents",
                                        "title": "Online registration documents",
                                        "widget": "file",
                                    },
                                },
                            ],
                            "variation": "default",
                        },
                    },
                    "blocks_layout": {
                        "items": [
                            "b03fb0aa-19e4-4bbf-8932-559f0fb22bc3",
                            "6e994da1-12f3-40df-a92c-f5a26b538d16",
                        ]
                    },
                    "title": "CCA Event details",
                },
                "1b1914bf-5b46-4baf-95a2-a02df27592e5": {
                    "@type": "tab",
                    "blocks": {
                        "58aa89ca-1c39-4a4d-8226-e53997291468": {
                            "@type": "metadataSection",
                            "fields": [
                                {
                                    "@id": "033d8dbe-5220-46dd-99f6-84906dc5c658",
                                    "field": {
                                        "id": "exclude_from_nav",
                                        "title": "Exclude from navigation",
                                        "widget": "boolean",
                                    },
                                },
                                {
                                    "@id": "1f56769e-0c64-4c2b-b080-803479d79ca7",
                                    "field": {
                                        "id": "allow_discussion",
                                        "title": "Allow discussion",
                                        "widget": "choices",
                                    },
                                },
                                {
                                    "@id": "b06824f1-60aa-454d-b546-6bd0fa17bb94",
                                    "field": {
                                        "id": "id",
                                        "title": "Short name",
                                        "widget": "string",
                                    },
                                },
                            ],
                            "variation": "default",
                        },
                        "ac411770-56de-4cb4-b88e-f762935bec09": {"@type": "slate"},
                    },
                    "blocks_layout": {
                        "items": [
                            "58aa89ca-1c39-4a4d-8226-e53997291468",
                            "ac411770-56de-4cb4-b88e-f762935bec09",
                        ]
                    },
                    "title": "Settings",
                },
                "7138bea1-5a99-469b-afcc-8d9c0e9ec5e1": {
                    "@type": "tab",
                    "blocks": {
                        "68ffaf40-87b1-489f-ade3-fcf3edb5d2f7": {
                            "@type": "metadataSection",
                            "fields": [
                                {
                                    "@id": "b2022a11-20d9-442b-901f-829787e0b93d",
                                    "field": {
                                        "id": "effective",
                                        "title": "Publishing Date",
                                        "widget": "datetime",
                                    },
                                },
                                {
                                    "@id": "cb90c225-e55d-4618-bf65-2c823999fae2",
                                    "field": {
                                        "id": "expires",
                                        "title": "Expiration Date",
                                        "widget": "datetime",
                                    },
                                },
                                {
                                    "@id": "c56e5491-20e9-4102-8f7b-8396f8047224",
                                    "field": {
                                        "id": "timezone",
                                        "title": "Timezone",
                                        "widget": "choices",
                                    },
                                },
                                {
                                    "@id": "92a93414-f7af-477f-bc6d-bdf34d6e60f8",
                                    "field": {
                                        "id": "title",
                                        "title": "Title",
                                        "widget": "title",
                                    },
                                },
                                {
                                    "@id": "fed322f4-abff-4421-b215-09d7b8de50ec",
                                    "field": {
                                        "id": "description",
                                        "title": "Summary",
                                        "widget": "description",
                                    },
                                },
                                {
                                    "@id": "ad98050a-331f-4215-aa0d-7a800ccdf982",
                                    "field": {
                                        "id": "contact_email",
                                        "title": "Contact E-mail",
                                        "widget": "string",
                                    },
                                },
                                {
                                    "@id": "66171230-a4c7-4f49-8662-a3e794cc2614",
                                    "field": {
                                        "id": "event_url",
                                        "title": "Event URL",
                                        "widget": "string",
                                    },
                                },
                                {
                                    "@id": "99361385-8f40-460e-bb2b-93d4323f2643",
                                    "field": {
                                        "id": "location",
                                        "title": "Location",
                                        "widget": "string",
                                    },
                                },
                                {
                                    "@id": "a67c2798-6359-4946-8e08-e29644d73781",
                                    "field": {
                                        "id": "start",
                                        "title": "Event Starts",
                                        "widget": "datetime",
                                    },
                                },
                                {
                                    "@id": "5695d47c-ed32-4dad-83dc-ea6212551323",
                                    "field": {
                                        "id": "end",
                                        "title": "Event Ends",
                                        "widget": "datetime",
                                    },
                                },
                                {
                                    "@id": "807bca1c-70e7-4b4b-856e-1cac4ffada0f",
                                    "field": {
                                        "id": "whole_day",
                                        "title": "Whole Day",
                                        "widget": "boolean",
                                    },
                                },
                                {
                                    "@id": "b5995664-c0fb-405e-a5e9-ff2bdb1cce68",
                                    "field": {
                                        "id": "open_end",
                                        "title": "Open End",
                                        "widget": "boolean",
                                    },
                                },
                                {
                                    "@id": "485f1159-3a96-408b-ab49-78bd22590399",
                                    "field": {
                                        "id": "changeNote",
                                        "title": "Change Note",
                                        "widget": "string",
                                    },
                                },
                                {
                                    "@id": "a0fd54ca-cdf5-4ca5-9bd3-cc1c6fc55b58",
                                    "field": {
                                        "id": "recurrence",
                                        "title": "Recurrence",
                                        "widget": "textarea",
                                    },
                                },
                                {
                                    "@id": "7a66a8e7-70da-42f4-b711-de48f2c97f2e",
                                    "field": {
                                        "id": "text",
                                        "title": "Text",
                                        "widget": "richtext",
                                    },
                                },
                            ],
                            "variation": "default",
                        },
                        "8db9fa99-1e65-45f1-b235-049bc3dbe970": {"@type": "slate"},
                    },
                    "blocks_layout": {
                        "items": [
                            "68ffaf40-87b1-489f-ade3-fcf3edb5d2f7",
                            "8db9fa99-1e65-45f1-b235-049bc3dbe970",
                        ]
                    },
                    "title": "Item Description",
                },
                "ab13d381-3f15-4915-a52b-86b46e544718": {
                    "@type": "tab",
                    "blocks": {
                        "1249ff8d-0fce-4a45-8854-37b22afc2b10": {
                            "@type": "metadataSection",
                            "fields": [
                                {
                                    "@id": "40186598-797f-433b-9bc8-25c283b2f5ff",
                                    "field": {
                                        "id": "subjects",
                                        "title": "Tags",
                                        "widget": "tags",
                                    },
                                },
                                {
                                    "@id": "48ef78c2-b973-41ac-bd8d-43619c939c9e",
                                    "field": {
                                        "id": "relatedItems",
                                        "title": "Related Items",
                                        "widget": "relations",
                                    },
                                },
                            ],
                            "variation": "default",
                        },
                        "3144f1bf-0b12-43fc-892d-21eda18b14e8": {"@type": "slate"},
                    },
                    "blocks_layout": {
                        "items": [
                            "1249ff8d-0fce-4a45-8854-37b22afc2b10",
                            "3144f1bf-0b12-43fc-892d-21eda18b14e8",
                        ]
                    },
                    "title": "Categorization",
                },
                "cb5a1b9b-4aeb-4f81-a67a-55ff9f9c1ff1": {
                    "@type": "tab",
                    "blocks": {
                        "8e923bd7-7b37-4584-bd2e-5ac094fe595d": {
                            "@type": "metadataSection",
                            "fields": [
                                {
                                    "@id": "ace4b99b-3afd-4448-a76a-6262346e1056",
                                    "field": {
                                        "id": "creators",
                                        "title": "Creators",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "e1d40dfb-0684-426a-b444-0b22c7a41e40",
                                    "field": {
                                        "id": "contributors",
                                        "title": "Contributors",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "847ec98d-eece-4512-9953-1eb234d59047",
                                    "field": {
                                        "id": "rights",
                                        "title": "Rights",
                                        "widget": "textarea",
                                    },
                                },
                            ],
                            "variation": "default",
                        },
                        "ec71858e-f7ef-465e-ae1f-c3e593266e79": {"@type": "slate"},
                    },
                    "blocks_layout": {
                        "items": [
                            "8e923bd7-7b37-4584-bd2e-5ac094fe595d",
                            "ec71858e-f7ef-465e-ae1f-c3e593266e79",
                        ]
                    },
                    "title": "Ownership",
                },
            },
            "blocks_layout": {
                "items": [
                    "7138bea1-5a99-469b-afcc-8d9c0e9ec5e1",
                    "1b1914bf-5b46-4baf-95a2-a02df27592e5",
                    "ab13d381-3f15-4915-a52b-86b46e544718",
                    "cb5a1b9b-4aeb-4f81-a67a-55ff9f9c1ff1",
                    "11dbdd53-8d3c-43ec-b04e-b88f4adfe418",
                ]
            },
        },
        "template": "default",
        "verticalAlign": "flex-start",
    },
}

cca_event_items = [
    "1d17872f-06a8-4460-809c-ab14435bafe0",
    "8c106f0d-0928-444b-b016-5dd78a2e0eab",
    "392b0b2b-85c5-4d36-9c61-262d759b7562",
]
