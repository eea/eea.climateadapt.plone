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

guidance_layout_blocks = {
    "02958cd6-97c8-42a2-8cf9-cc50379d77c7": {
        "@type": "tabs_block",
        "data": {
            "blocks": {
                "2d3795ad-fb5f-4de6-806a-ccc1aa8454b4": {
                    "@type": "tab",
                    "blocks": {
                        "9bcf7259-5e76-4f3a-ac03-5e47579a50c8": {"@type": "slate"},
                        "b226cdc5-d6be-4e7f-9e9d-2b712b212c4e": {
                            "@type": "metadataSection",
                            "fields": [
                                {
                                    "@id": "1dc5888a-1c57-44c0-970b-5bcd748d6cd2",
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
                            "b226cdc5-d6be-4e7f-9e9d-2b712b212c4e",
                            "9bcf7259-5e76-4f3a-ac03-5e47579a50c8",
                        ]
                    },
                    "title": "Geographic info",
                },
                "5c6d883f-133e-4cfa-a056-0887c623e4ed": {
                    "@type": "tab",
                    "blocks": {
                        "4fb588eb-96c0-454b-99f4-3d50661c2721": {"@type": "slate"},
                        "a1dcd207-2806-452e-9f8d-614b419117c2": {
                            "@type": "metadataSection",
                            "fields": [
                                {
                                    "@id": "6a6acf75-5de7-4f95-9e24-d48eee2bb3ed",
                                    "field": {
                                        "id": "include_in_observatory",
                                        "title": "Include in observatory",
                                        "widget": "boolean",
                                    },
                                },
                                {
                                    "@id": "1345cf19-7e56-4b45-90b1-f95e532dca0e",
                                    "field": {
                                        "id": "include_in_mission",
                                        "title": "Include in the Mission Portal",
                                        "widget": "boolean",
                                    },
                                },
                                {
                                    "@id": "d2f9c9fe-97b1-47ca-83e4-96625050d4a5",
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
                            "a1dcd207-2806-452e-9f8d-614b419117c2",
                            "4fb588eb-96c0-454b-99f4-3d50661c2721",
                        ]
                    },
                    "title": "Inclusion in subsites",
                },
                "940c762e-d8b5-4b65-bfcb-a28af74b9b4b": {
                    "@type": "tab",
                    "blocks": {
                        "69c5c473-99c3-4614-8536-886f327201f8": {"@type": "slate"},
                        "bca44002-9f20-41ed-ae17-376fbaa69368": {
                            "@type": "metadataSection",
                            "fields": [
                                {
                                    "@id": "0d5846ca-de1d-42a9-bd1f-520d3499fbfd",
                                    "field": {
                                        "id": "publication_date",
                                        "title": "Date of item's publication",
                                        "widget": "date",
                                    },
                                },
                                {
                                    "@id": "d690b90e-3dd3-4755-a680-e9ca872ea7f0",
                                    "field": {
                                        "id": "title",
                                        "title": "Title",
                                        "widget": "title",
                                    },
                                    "showLabel": False,
                                },
                                {
                                    "@id": "9bbc91c5-8fa3-4ad9-add4-245f51b41674",
                                    "field": {
                                        "id": "description",
                                        "title": "Short summary",
                                        "widget": "description",
                                    },
                                },
                                {
                                    "@id": "4b60344e-b001-4fc9-8da3-bd0089fb1787",
                                    "field": {
                                        "id": "long_description",
                                        "title": "Description",
                                        "widget": "richtext",
                                    },
                                },
                                {
                                    "@id": "e131cb87-692d-4864-9ce4-b8b9bbb1b714",
                                    "field": {
                                        "id": "keywords",
                                        "title": "Keywords",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "cfff27a1-402b-43d3-8080-ad2ce83acf90",
                                    "field": {
                                        "id": "sectors",
                                        "title": "Sectors",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "aa373445-07ee-4752-aa99-cb0b9a18b9fa",
                                    "field": {
                                        "id": "climate_impacts",
                                        "title": "Climate impacts",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "7c245917-1622-4dcf-ad37-ff6375264e06",
                                    "field": {
                                        "id": "elements",
                                        "title": "Adaptation elements",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "347c88c6-3c37-431b-a3e7-ada15c068d2b",
                                    "field": {
                                        "id": "logo",
                                        "title": "Logo",
                                        "widget": "image",
                                    },
                                },
                                {
                                    "@id": "6c1431fa-5e95-41a5-aa04-b281ae11908a",
                                    "field": {
                                        "id": "image",
                                        "title": "Thumbnail",
                                        "widget": "image",
                                    },
                                },
                                {
                                    "@id": "7923d2a9-115e-4d34-a239-e53d0c1c87a3",
                                    "field": {
                                        "id": "origin_website",
                                        "title": "Item from third parties",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "bca40b94-aa98-4be7-a412-1e89619e434e",
                                    "field": {
                                        "id": "contributor_list",
                                        "title": "Contributor(s)",
                                        "widget": "relations",
                                    },
                                },
                                {
                                    "@id": "1b92dc88-cdd7-431a-9109-657a871857da",
                                    "field": {
                                        "id": "other_contributor",
                                        "title": "Other contributor(s)",
                                        "widget": "textarea",
                                    },
                                },
                            ],
                            "variation": "default",
                        },
                    },
                    "blocks_layout": {
                        "items": [
                            "bca44002-9f20-41ed-ae17-376fbaa69368",
                            "69c5c473-99c3-4614-8536-886f327201f8",
                        ]
                    },
                    "title": "Item Description",
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
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "02dd09fb-cbd1-4ba1-b4a8-27d0c286c0d0",
                                    "field": {
                                        "id": "source",
                                        "title": "References",
                                        "widget": "richtext",
                                    },
                                },
                                {
                                    "@id": "eaf78bfc-b093-4886-b26e-137ba1e805ec",
                                    "field": {
                                        "id": "special_tags",
                                        "title": "Special tagging",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "f2ac2370-7e05-4127-b787-8b3bdf6aa718",
                                    "field": {
                                        "id": "comments",
                                        "title": "Comments",
                                        "widget": "textarea",
                                    },
                                },
                                {
                                    "@id": "7da60aa8-229f-4a6b-841b-d697cd679658",
                                    "field": {
                                        "id": "relatedItems",
                                        "title": "Related Items",
                                        "widget": "relations",
                                    },
                                },
                            ],
                            "variation": "default",
                        },
                        "dc8a63a6-8bf7-485c-9044-c520ca6cfbd3": {"@type": "slate"},
                    },
                    "blocks_layout": {
                        "items": [
                            "8b73e4a3-dc96-4287-a8dd-1b5e6c8bd098",
                            "dc8a63a6-8bf7-485c-9044-c520ca6cfbd3",
                        ]
                    },
                    "title": "Reference info",
                },
            },
            "blocks_layout": {
                "items": [
                    "940c762e-d8b5-4b65-bfcb-a28af74b9b4b",
                    "941a4acc-7de7-484f-b848-b2e1e5bcf724",
                    "2d3795ad-fb5f-4de6-806a-ccc1aa8454b4",
                    "5c6d883f-133e-4cfa-a056-0887c623e4ed",
                ]
            },
        },
        "template": "default",
        "verticalAlign": "flex-start",
    },
    "145aa113-bf4a-4546-9612-864b50e5ab50": {
        "@type": "title",
        "copyrightIcon": "ri-copyright-line",
    },
    "5f508e99-7478-46fb-9fdd-51ca71ba0844": {
        "@type": "slate",
        "plaintext": "",
        "value": [{"children": [{"text": ""}], "type": "p"}],
    },
}

guidance_layout_items = [
    "145aa113-bf4a-4546-9612-864b50e5ab50",
    "02958cd6-97c8-42a2-8cf9-cc50379d77c7",
    "5f508e99-7478-46fb-9fdd-51ca71ba0844",
]

organisation_layout_blocks = {
    "873aee9d-23fd-4a8e-aa82-7e53e36142a7": {
        "@type": "title",
        "copyrightIcon": "ri-copyright-line",
    },
    "e7e101d3-0a6a-4976-8b0a-ab7603c642a9": {
        "@type": "tabs_block",
        "data": {
            "blocks": {
                "cce027cd-5299-4c9a-80cf-b7a482df420b": {
                    "@type": "tab",
                    "blocks": {
                        "1d4d73b0-618c-4c8b-a46b-1a924f98f4ac": {"@type": "slate"},
                        "6c34c28b-61fc-4381-957c-9e90e03d414a": {
                            "@type": "metadataSection",
                            "fields": [
                                {
                                    "@id": "c5b73741-add2-4ae8-a725-7cd29f0d6761",
                                    "field": {
                                        "id": "websites",
                                        "title": "Websites",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "0020812e-8306-403d-a7bb-2755eff143d4",
                                    "field": {
                                        "id": "special_tags",
                                        "title": "Special tagging",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "1501d18c-8c37-47aa-8b80-62e586b25219",
                                    "field": {
                                        "id": "relatedItems",
                                        "title": "Related Items",
                                        "widget": "relations",
                                    },
                                },
                                {
                                    "@id": "9a3e06db-50fa-4021-b42e-5447a954b99d",
                                    "field": {
                                        "id": "comments",
                                        "title": "Comments",
                                        "widget": "textarea",
                                    },
                                },
                            ],
                            "variation": "default",
                        },
                    },
                    "blocks_layout": {
                        "items": [
                            "6c34c28b-61fc-4381-957c-9e90e03d414a",
                            "1d4d73b0-618c-4c8b-a46b-1a924f98f4ac",
                        ]
                    },
                    "title": "Reference info",
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
                                        "widget": "textarea",
                                    },
                                }
                            ],
                            "variation": "default",
                        },
                        "c46aa30b-e9d7-4536-b0d2-f5ab4da99fbf": {"@type": "slate"},
                    },
                    "blocks_layout": {
                        "items": [
                            "8ebe1709-c8c1-44e0-9e43-f9bd50223656",
                            "c46aa30b-e9d7-4536-b0d2-f5ab4da99fbf",
                        ]
                    },
                    "title": "Geographic info",
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
                                        "widget": "date",
                                    },
                                },
                                {
                                    "@id": "c1a6479a-ee17-4ba5-a1cf-a1b5518bd194",
                                    "field": {
                                        "id": "acronym",
                                        "title": "Acronym",
                                        "widget": "string",
                                    },
                                },
                                {
                                    "@id": "97fca98f-d401-4609-be06-75dc246565a5",
                                    "field": {
                                        "id": "title",
                                        "title": "Name",
                                        "widget": "title",
                                    },
                                },
                                {
                                    "@id": "13584695-1b5d-46d2-93df-0ad0147f3824",
                                    "field": {
                                        "id": "description",
                                        "title": "Short summary",
                                        "widget": "description",
                                    },
                                },
                                {
                                    "@id": "6c175970-4be3-4592-8e4c-17aed8477c96",
                                    "field": {
                                        "id": "long_description",
                                        "title": "Description",
                                        "widget": "richtext",
                                    },
                                },
                                {
                                    "@id": "139c3d4d-d2d5-43c7-b923-4308ae2176db",
                                    "field": {
                                        "id": "keywords",
                                        "title": "Keywords",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "9bf95e74-c573-4df4-a70f-6779cd2194fc",
                                    "field": {
                                        "id": "sectors",
                                        "title": "Sectors",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "85e57766-dd24-46a8-a488-c256a01a8abd",
                                    "field": {
                                        "id": "climate_impacts",
                                        "title": "Climate impacts",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "0906e2fe-00e4-476e-82d3-5b3ac3571a20",
                                    "field": {
                                        "id": "elements",
                                        "title": "Adaptation elements",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "5224bb84-8f89-4bd1-be21-1e02bd3f0d02",
                                    "field": {
                                        "id": "logo",
                                        "title": "Logo",
                                        "widget": "image",
                                    },
                                },
                                {
                                    "@id": "eed21c12-3400-4132-a814-c5205c9f50a9",
                                    "field": {
                                        "id": "image",
                                        "title": "Thumbnail",
                                        "widget": "image",
                                    },
                                },
                                {
                                    "@id": "d572121f-aaff-43cd-b989-3d217fcf7921",
                                    "field": {
                                        "id": "origin_website",
                                        "title": "Item from third parties",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "3ef3c28d-3669-4ff8-a337-0ef7b3597ac7",
                                    "field": {
                                        "id": "contact",
                                        "title": "Contact",
                                        "widget": "string",
                                    },
                                },
                            ],
                            "variation": "default",
                        },
                        "c2913a3f-e4d1-481d-a086-f7f05ef39751": {
                            "@type": "slate",
                            "plaintext": "",
                            "value": [{"children": [{"text": ""}], "type": "p"}],
                        },
                    },
                    "blocks_layout": {
                        "items": [
                            "345db6db-1783-4bc2-a0e7-578b2d98e319",
                            "c2913a3f-e4d1-481d-a086-f7f05ef39751",
                        ]
                    },
                    "title": "Item description",
                },
                "e72ad0f9-e9eb-473a-bf07-3e05d4a15135": {
                    "@type": "tab",
                    "blocks": {
                        "c565b4f3-e11e-46ba-8a38-0faa1ca3d4b8": {"@type": "slate"},
                        "c6a2ec54-c105-4845-9190-2cc3e5bb31d8": {
                            "@type": "metadataSection",
                            "fields": [
                                {
                                    "@id": "1b240cfd-65ac-4020-85d3-90852f9cfed8",
                                    "field": {
                                        "id": "include_in_observatory",
                                        "title": "Include in observatory",
                                        "widget": "boolean",
                                    },
                                },
                                {
                                    "@id": "7f60ebe8-bfbf-4da2-8a53-a617599774c3",
                                    "field": {
                                        "id": "include_in_mission",
                                        "title": "Include in the Mission Portal",
                                        "widget": "boolean",
                                    },
                                },
                                {
                                    "@id": "eb6c5476-77d6-41b7-b8f9-74bdfc79c1c3",
                                    "field": {
                                        "id": "organisational_key_activities",
                                        "title": "Key activities within climate change and health (relevant for the Observatory)",
                                        "widget": "richtext",
                                    },
                                },
                                {
                                    "@id": "73b81b92-147f-46b6-9952-b25a76278d1e",
                                    "field": {
                                        "id": "organisational_websites",
                                        "title": "Links to further information (relevant for the Observatory)",
                                        "widget": "richtext",
                                    },
                                },
                                {
                                    "@id": "94f47853-ee98-409a-8f3e-11c8cec37466",
                                    "field": {
                                        "id": "organisational_contact_information",
                                        "title": "Contact information (relevant for the Observatory)",
                                        "widget": "richtext",
                                    },
                                },
                            ],
                            "variation": "default",
                        },
                    },
                    "blocks_layout": {
                        "items": [
                            "c6a2ec54-c105-4845-9190-2cc3e5bb31d8",
                            "c565b4f3-e11e-46ba-8a38-0faa1ca3d4b8",
                        ]
                    },
                    "title": "Inclusion in subsites",
                },
            },
            "blocks_layout": {
                "items": [
                    "e30dbfb7-7108-4df2-9b7e-3ea782f1839d",
                    "cce027cd-5299-4c9a-80cf-b7a482df420b",
                    "d3c6f26c-1614-4fa4-84b8-32fa1d991b80",
                    "e72ad0f9-e9eb-473a-bf07-3e05d4a15135",
                ]
            },
        },
        "template": "default",
        "verticalAlign": "flex-start",
    },
}

organisation_layout_items = [
    "873aee9d-23fd-4a8e-aa82-7e53e36142a7",
    "e7e101d3-0a6a-4976-8b0a-ab7603c642a9",
]

publication_layout_blocks = {
    "87949dc6-ca21-4f7c-8dc9-f0a599b106d3": {"@type": "slate"},
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
                                        "widget": "date",
                                    },
                                },
                                {
                                    "@id": "bf893209-1f93-4301-98d8-69ce308448d8",
                                    "field": {
                                        "id": "title",
                                        "title": "Title",
                                        "widget": "title",
                                    },
                                },
                                {
                                    "@id": "a394626e-6ac4-4e64-8779-12323049c856",
                                    "field": {
                                        "id": "description",
                                        "title": "Short summary",
                                        "widget": "description",
                                    },
                                },
                                {
                                    "@id": "1de9ae1c-4faf-4a6e-966d-6f6f4554fa5f",
                                    "field": {
                                        "id": "long_description",
                                        "title": "Description",
                                        "widget": "richtext",
                                    },
                                },
                                {
                                    "@id": "153f23dd-933e-45ad-9066-2b6753b21346",
                                    "field": {
                                        "id": "keywords",
                                        "title": "Keywords",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "68615032-0585-4e25-b36d-4500ea7334e5",
                                    "field": {
                                        "id": "sectors",
                                        "title": "Sectors",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "8bc5432b-1c9c-4be2-a5a8-f0d97c56aeff",
                                    "field": {
                                        "id": "climate_impacts",
                                        "title": "Climate impacts",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "ddbdb253-cca9-4f03-bd9e-d2ecd4c54110",
                                    "field": {
                                        "id": "elements",
                                        "title": "Adaptation elements",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "d267ea61-bd30-46e7-9709-896da834b303",
                                    "field": {
                                        "id": "logo",
                                        "title": "Logo",
                                        "widget": "image",
                                    },
                                },
                                {
                                    "@id": "3886e6b8-0fef-4d31-a4fc-261266531b66",
                                    "field": {
                                        "id": "image",
                                        "title": "Thumbnail",
                                        "widget": "image",
                                    },
                                },
                                {
                                    "@id": "dd2822cf-1892-4c5c-9881-c0ad1a67ff30",
                                    "field": {
                                        "id": "origin_website",
                                        "title": "Item from third parties",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "4af85da4-3c32-4e75-b56e-393e3704ef4c",
                                    "field": {
                                        "id": "contributor_list",
                                        "title": "Contributor(s)",
                                        "widget": "relations",
                                    },
                                },
                                {
                                    "@id": "43aa3122-e220-4455-ba31-2b4a278d66a4",
                                    "field": {
                                        "id": "other_contributor",
                                        "title": "Other contributor(s)",
                                        "widget": "textarea",
                                    },
                                },
                            ],
                            "variation": "default",
                        },
                        "fef8785a-a894-4ec9-95a8-f3fd57a57578": {"@type": "slate"},
                    },
                    "blocks_layout": {
                        "items": [
                            "794f2ccf-edb4-4086-9af7-6185c2086708",
                            "fef8785a-a894-4ec9-95a8-f3fd57a57578",
                        ]
                    },
                    "title": "Item description",
                },
                "11094ac9-d04c-45f2-8b69-5e0f2054c450": {
                    "@type": "tab",
                    "blocks": {
                        "065ade50-40f6-4361-b7db-f7fc5d4d0ce3": {"@type": "slate"},
                        "8fc54b45-d282-45e2-ae1f-d5dcd1608be4": {
                            "@type": "metadataSection",
                            "fields": [
                                {
                                    "@id": "d2252de2-0226-408b-bc14-7eef12e125d1",
                                    "field": {
                                        "id": "websites",
                                        "title": "Websites",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "2e6e2b03-8aaf-40af-84fc-1783d14afa25",
                                    "field": {
                                        "id": "source",
                                        "title": "References",
                                        "widget": "richtext",
                                    },
                                },
                                {
                                    "@id": "d79fc04d-ea8f-46ef-b576-387e342c69ee",
                                    "field": {
                                        "id": "special_tags",
                                        "title": "Special tagging",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "eb06b267-6a00-40b9-86cb-eda08c3aae2f",
                                    "field": {
                                        "id": "comments",
                                        "title": "Comments",
                                        "widget": "textarea",
                                    },
                                },
                                {
                                    "@id": "a476f18e-2d27-4eb1-9793-6581c8ab78da",
                                    "field": {
                                        "id": "relatedItems",
                                        "title": "Related Items",
                                        "widget": "relations",
                                    },
                                },
                            ],
                            "variation": "default",
                        },
                    },
                    "blocks_layout": {
                        "items": [
                            "8fc54b45-d282-45e2-ae1f-d5dcd1608be4",
                            "065ade50-40f6-4361-b7db-f7fc5d4d0ce3",
                        ]
                    },
                    "title": "Reference info",
                },
                "3e1c86fb-29b8-4606-9671-94f4e18bf951": {
                    "@type": "tab",
                    "blocks": {
                        "210fc730-b795-4002-a5f0-9c0fba7200c4": {"@type": "slate"},
                        "eaa796a3-ab2a-4684-86ea-fd8a74542dda": {
                            "@type": "metadataSection",
                            "fields": [
                                {
                                    "@id": "412c26c9-ca67-4622-b9aa-f1fa4c7bbab2",
                                    "field": {
                                        "id": "include_in_observatory",
                                        "title": "Include in observatory",
                                        "widget": "boolean",
                                    },
                                },
                                {
                                    "@id": "d505c418-6650-43d8-a81c-f126797a26ef",
                                    "field": {
                                        "id": "include_in_mission",
                                        "title": "Include in the Mission Portal",
                                        "widget": "boolean",
                                    },
                                },
                                {
                                    "@id": "e424bf22-2c39-4ebe-b52f-98fe8059e8da",
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
                            "eaa796a3-ab2a-4684-86ea-fd8a74542dda",
                            "210fc730-b795-4002-a5f0-9c0fba7200c4",
                        ]
                    },
                    "title": "Include in subsites",
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
                                        "widget": "textarea",
                                    },
                                }
                            ],
                            "variation": "default",
                        },
                        "bba516ef-c34b-45ef-b1cc-1eecc154f433": {"@type": "slate"},
                    },
                    "blocks_layout": {
                        "items": [
                            "96058a9b-5c97-45c8-a5c5-c8d5dff5bcb3",
                            "bba516ef-c34b-45ef-b1cc-1eecc154f433",
                        ]
                    },
                    "title": "Geographic info",
                },
            },
            "blocks_layout": {
                "items": [
                    "0bc447c1-e867-46df-90dd-5a085665b1f6",
                    "11094ac9-d04c-45f2-8b69-5e0f2054c450",
                    "c405ddc3-596c-47c1-9cf4-2f59aa4f214e",
                    "3e1c86fb-29b8-4606-9671-94f4e18bf951",
                ]
            },
        },
        "template": "default",
        "verticalAlign": "flex-start",
    },
    "bfac63ff-6a8c-435c-aad9-32f157903402": {
        "@type": "title",
        "copyrightIcon": "ri-copyright-line",
    },
}

publication_layout_items = [
    "bfac63ff-6a8c-435c-aad9-32f157903402",
    "aef32685-1aaf-440f-b48b-3379da51ef74",
    "87949dc6-ca21-4f7c-8dc9-f0a599b106d3",
]

research_layout_blocks = {
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
                                        "widget": "textarea",
                                    },
                                }
                            ],
                            "variation": "default",
                        },
                        "eefa935b-53db-49a0-80dd-8bf518abcf18": {"@type": "slate"},
                    },
                    "blocks_layout": {
                        "items": [
                            "1e6a5735-1097-4fd0-b663-79ec34d474c2",
                            "eefa935b-53db-49a0-80dd-8bf518abcf18",
                        ]
                    },
                    "title": "Geographic info",
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
                                        "widget": "date",
                                    },
                                },
                                {
                                    "@id": "4d491aa2-6a38-4bc9-9989-997369583019",
                                    "field": {
                                        "id": "title",
                                        "title": "Title",
                                        "widget": "title",
                                    },
                                },
                                {
                                    "@id": "eeb4b6ca-ada5-47bd-88bd-a3960912e458",
                                    "field": {
                                        "id": "description",
                                        "title": "Short summary",
                                        "widget": "description",
                                    },
                                },
                                {
                                    "@id": "5a4f7f60-9c9d-4ec0-8e95-ed49765c05a2",
                                    "field": {
                                        "id": "long_description",
                                        "title": "Description",
                                        "widget": "richtext",
                                    },
                                },
                                {
                                    "@id": "f151d6be-20c1-4739-a0f2-c358dabc365e",
                                    "field": {
                                        "id": "keywords",
                                        "title": "Keywords",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "31575864-3b67-47f1-8200-e5d09bb9d688",
                                    "field": {
                                        "id": "sectors",
                                        "title": "Sectors",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "5cd169bb-60a1-411e-b552-6e7e378bf29b",
                                    "field": {
                                        "id": "climate_impacts",
                                        "title": "Climate impacts",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "5450efc7-29a2-44ea-afd6-ecd1745b257b",
                                    "field": {
                                        "id": "elements",
                                        "title": "Adaptation elements",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "2c452f75-5a5a-4f16-b9ba-ef4127c67f4e",
                                    "field": {
                                        "id": "logo",
                                        "title": "Logo",
                                        "widget": "image",
                                    },
                                },
                                {
                                    "@id": "01132e31-15c4-44f3-9fdf-66a9cc087e60",
                                    "field": {
                                        "id": "image",
                                        "title": "Thumbnail",
                                        "widget": "image",
                                    },
                                },
                                {
                                    "@id": "7627a4a6-6927-4569-a061-32c13915d1e2",
                                    "field": {
                                        "id": "origin_website",
                                        "title": "Item from third parties",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "a656fef1-3bad-4d03-8ef4-87abfa8cd666",
                                    "field": {
                                        "id": "contributor_list",
                                        "title": "Contributor(s)",
                                        "widget": "relations",
                                    },
                                },
                                {
                                    "@id": "5e9aecc6-3d0e-4088-b641-9ce30d5a67cd",
                                    "field": {
                                        "id": "other_contributor",
                                        "title": "Other contributor(s)",
                                        "widget": "textarea",
                                    },
                                },
                            ],
                            "variation": "default",
                        },
                        "beb01a1b-68cc-4911-abbb-56ff5cbd54d5": {"@type": "slate"},
                    },
                    "blocks_layout": {
                        "items": [
                            "6ced4b27-fa65-4627-926a-b2e6588265e6",
                            "beb01a1b-68cc-4911-abbb-56ff5cbd54d5",
                        ]
                    },
                    "title": "Item description",
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
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "3a5688d4-899b-4a37-9a9d-bb7d0fa53afc",
                                    "field": {
                                        "id": "source",
                                        "title": "References",
                                        "widget": "richtext",
                                    },
                                },
                                {
                                    "@id": "b0861919-1acf-483f-a9f4-da5c7c9a21d2",
                                    "field": {
                                        "id": "special_tags",
                                        "title": "Special tagging",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "e1cfd8e4-1a76-42cb-aab7-299f8b6ef4c1",
                                    "field": {
                                        "id": "comments",
                                        "title": "Comments",
                                        "widget": "textarea",
                                    },
                                },
                            ],
                            "variation": "default",
                        },
                        "f6cd76ef-ce0b-4d95-bcc5-45d4ef5b104f": {
                            "@type": "slate",
                            "plaintext": "",
                            "value": [{"children": [{"text": ""}], "type": "p"}],
                        },
                    },
                    "blocks_layout": {
                        "items": [
                            "2c494947-79f9-4dfe-b916-3049ddd909db",
                            "f6cd76ef-ce0b-4d95-bcc5-45d4ef5b104f",
                        ]
                    },
                    "title": "Reference info",
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
                                        "widget": "string",
                                    },
                                }
                            ],
                            "variation": "default",
                        },
                        "23273133-eb8c-4131-93cc-06f218a5facc": {"@type": "slate"},
                    },
                    "blocks_layout": {
                        "items": [
                            "22b7793b-e74f-458e-9cae-de0b5f9dc8d0",
                            "23273133-eb8c-4131-93cc-06f218a5facc",
                        ]
                    },
                    "title": "Settings",
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
                                        "widget": "boolean",
                                    },
                                },
                                {
                                    "@id": "cd570c10-39fe-44cb-8c7c-7790c8234866",
                                    "field": {
                                        "id": "include_in_mission",
                                        "title": "Include in the Mission Portal",
                                        "widget": "boolean",
                                    },
                                },
                                {
                                    "@id": "2053539e-5df2-4438-bf85-2c20aa0e59cf",
                                    "field": {
                                        "id": "health_impacts",
                                        "title": "Health impacts",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "941b1ab8-539e-48cf-a867-35c26772646a",
                                    "field": {
                                        "id": "relatedItems",
                                        "title": "Related Items",
                                        "widget": "relations",
                                    },
                                },
                            ],
                            "variation": "default",
                        },
                        "c23d72f2-df42-4c86-b4d2-eef84bf76392": {"@type": "slate"},
                    },
                    "blocks_layout": {
                        "items": [
                            "0496d4d7-61b2-4d81-a581-ceb0ec93dfc2",
                            "c23d72f2-df42-4c86-b4d2-eef84bf76392",
                        ]
                    },
                    "title": "Inclusion in subsites",
                },
            },
            "blocks_layout": {
                "items": [
                    "2115ee00-bf5d-4398-b83a-84f55f67b730",
                    "863e2919-3f3c-4d14-a1d7-a7aa9c67c005",
                    "0c0b33a9-a7eb-4247-b891-98e033356f69",
                    "c2cb64c5-780b-47cc-ac87-7efcfb63623a",
                    "b6bff40e-3eaf-4782-af3e-d91d9c823f07",
                ]
            },
        },
        "template": "default",
        "verticalAlign": "flex-start",
    },
    "41c49483-40d2-4c61-a9df-4972609c6c38": {
        "@type": "title",
        "copyrightIcon": "ri-copyright-line",
    },
    "a804a94a-d173-497d-ac7d-b33c4433821d": {
        "@type": "slate",
        "plaintext": "",
        "value": [{"children": [{"text": ""}], "type": "p"}],
    },
}

research_layout_items = [
    "41c49483-40d2-4c61-a9df-4972609c6c38",
    "24bfc346-94c4-4b44-8c58-c4f72a2eb964",
    "a804a94a-d173-497d-ac7d-b33c4433821d",
]

tool_layout_blocks = {
    "613a783e-8652-410c-b57e-08e96913e0f2": {
        "@type": "tabs_block",
        "data": {
            "blocks": {
                "796a3ca2-3fd1-41db-a6ff-b28999360212": {
                    "@type": "tab",
                    "blocks": {
                        "9897e1b5-01a3-4174-b7ec-0624f43c9346": {"@type": "slate"},
                        "ff371fbc-61bb-4df9-9876-5f8ee9750c94": {
                            "@type": "metadataSection",
                            "fields": [
                                {
                                    "@id": "032c01de-aa1e-4b55-a656-b66e3fc8526f",
                                    "field": {
                                        "id": "include_in_observatory",
                                        "title": "Include in observatory",
                                        "widget": "boolean",
                                    },
                                },
                                {
                                    "@id": "ae75789f-0ce5-433b-9819-02daf8e34bb5",
                                    "field": {
                                        "id": "include_in_mission",
                                        "title": "Include in the Mission Portal",
                                        "widget": "boolean",
                                    },
                                },
                                {
                                    "@id": "f0d1c689-f85d-490a-9000-5f14298dddec",
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
                            "ff371fbc-61bb-4df9-9876-5f8ee9750c94",
                            "9897e1b5-01a3-4174-b7ec-0624f43c9346",
                        ]
                    },
                    "title": "Inclusion in subsites",
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
                                        "widget": "textarea",
                                    },
                                }
                            ],
                            "variation": "default",
                        },
                        "d9271d2e-372f-4761-b114-7c65de88840a": {"@type": "slate"},
                    },
                    "blocks_layout": {
                        "items": [
                            "1c7402ac-d908-4bbf-b712-3c54ccb1d58e",
                            "d9271d2e-372f-4761-b114-7c65de88840a",
                        ]
                    },
                    "title": "Geographic info",
                },
                "9d325a25-3493-43a2-8f1d-b26ab911bb91": {
                    "@type": "tab",
                    "blocks": {
                        "3e6b9302-0683-4a41-9843-5ab6c0e13978": {"@type": "slate"},
                        "f3ba3e54-5e62-4283-9283-e391f3411705": {
                            "@type": "metadataSection",
                            "fields": [
                                {
                                    "@id": "c9eb933e-4b5a-43ef-825d-a9aad3bb1140",
                                    "field": {
                                        "id": "websites",
                                        "title": "Websites",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "bf07141e-942c-41b0-bd58-49e1be179cc6",
                                    "field": {
                                        "id": "source",
                                        "title": "References",
                                        "widget": "richtext",
                                    },
                                },
                                {
                                    "@id": "e8b5d353-4868-4d70-b0ff-7dac4e84ac4f",
                                    "field": {
                                        "id": "special_tags",
                                        "title": "Special tagging",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "1375eb13-47e5-498c-b7a0-e1420d6fc2ee",
                                    "field": {
                                        "id": "comments",
                                        "title": "Comments",
                                        "widget": "textarea",
                                    },
                                },
                                {
                                    "@id": "43f1e56f-b331-437a-862f-7cfd6adbf275",
                                    "field": {
                                        "id": "relatedItems",
                                        "title": "Related Items",
                                        "widget": "relations",
                                    },
                                },
                            ],
                            "variation": "default",
                        },
                    },
                    "blocks_layout": {
                        "items": [
                            "f3ba3e54-5e62-4283-9283-e391f3411705",
                            "3e6b9302-0683-4a41-9843-5ab6c0e13978",
                        ]
                    },
                    "title": "Reference info",
                },
                "d51a9bc2-bf1a-4a44-bb55-6d60cbfa734d": {
                    "@type": "tab",
                    "blocks": {
                        "6d53b234-46ff-4907-8a5a-f046f4036705": {"@type": "slate"},
                        "e771001c-46bb-4bb8-bff1-3727ec852b32": {
                            "@type": "metadataSection",
                            "fields": [
                                {
                                    "@id": "d33d00df-e090-4c3b-8a10-e77c1d43bc8c",
                                    "field": {
                                        "id": "publication_date",
                                        "title": "Date of item's creation",
                                        "widget": "date",
                                    },
                                },
                                {
                                    "@id": "d1c11d2d-7452-495e-a19d-3b677bab9081",
                                    "field": {
                                        "id": "title",
                                        "title": "Title",
                                        "widget": "title",
                                    },
                                },
                                {
                                    "@id": "c101cc6d-1368-4f67-9d39-29dbdc35b839",
                                    "field": {
                                        "id": "description",
                                        "title": "Short summary",
                                        "widget": "description",
                                    },
                                },
                                {
                                    "@id": "e229c642-c45b-4556-be8b-a76d0b1dfaf0",
                                    "field": {
                                        "id": "long_description",
                                        "title": "Description",
                                        "widget": "richtext",
                                    },
                                },
                                {
                                    "@id": "a34af168-b8bf-42b3-906d-d3f95fcebf25",
                                    "field": {
                                        "id": "keywords",
                                        "title": "Keywords",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "86a2172d-54e7-4d3b-8648-c87e2ef4e661",
                                    "field": {
                                        "id": "sectors",
                                        "title": "Sectors",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "4825ba9b-a803-479c-8fb1-9169149c117e",
                                    "field": {
                                        "id": "climate_impacts",
                                        "title": "Climate impacts",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "7a399cd9-7b68-4127-bc72-1bcc1ec86be2",
                                    "field": {
                                        "id": "elements",
                                        "title": "Adaptation elements",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "9390f62c-da9b-46ef-8713-9b9ee95a2e84",
                                    "field": {
                                        "id": "logo",
                                        "title": "Logo",
                                        "widget": "image",
                                    },
                                },
                                {
                                    "@id": "68f28cab-e3e9-4926-858a-bd4438f3cb56",
                                    "field": {
                                        "id": "image",
                                        "title": "Thumbnail",
                                        "widget": "image",
                                    },
                                },
                                {
                                    "@id": "4648ffd1-85b3-43b9-9089-c8c1ab828c61",
                                    "field": {
                                        "id": "origin_website",
                                        "title": "Item from third parties",
                                        "widget": "array",
                                    },
                                },
                                {
                                    "@id": "50348533-4cb9-4e8b-9ceb-9024a41aedc0",
                                    "field": {
                                        "id": "contributor_list",
                                        "title": "Contributor(s)",
                                        "widget": "relations",
                                    },
                                },
                                {
                                    "@id": "f580799f-61f0-47f4-9fb7-9ffdb39c3adb",
                                    "field": {
                                        "id": "other_contributor",
                                        "title": "Other contributor(s)",
                                        "widget": "textarea",
                                    },
                                },
                            ],
                            "variation": "default",
                        },
                    },
                    "blocks_layout": {
                        "items": [
                            "e771001c-46bb-4bb8-bff1-3727ec852b32",
                            "6d53b234-46ff-4907-8a5a-f046f4036705",
                        ]
                    },
                    "title": "Item Description",
                },
            },
            "blocks_layout": {
                "items": [
                    "d51a9bc2-bf1a-4a44-bb55-6d60cbfa734d",
                    "9d325a25-3493-43a2-8f1d-b26ab911bb91",
                    "7c25e37c-0502-4970-8102-2529e827af30",
                    "796a3ca2-3fd1-41db-a6ff-b28999360212",
                ]
            },
        },
        "template": "default",
        "verticalAlign": "flex-start",
    },
    "72eff79b-8c00-44f1-98b9-16fcca2a3f03": {
        "@type": "slate",
        "plaintext": "",
        "value": [{"children": [{"text": ""}], "type": "p"}],
    },
    "96854e5f-1b23-484a-b009-d3a8523b2b43": {
        "@type": "title",
        "copyrightIcon": "ri-copyright-line",
    },
}

tool_layout_items = [
    "96854e5f-1b23-484a-b009-d3a8523b2b43",
    "613a783e-8652-410c-b57e-08e96913e0f2",
    "72eff79b-8c00-44f1-98b9-16fcca2a3f03",
]
