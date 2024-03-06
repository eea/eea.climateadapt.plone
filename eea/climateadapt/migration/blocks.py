from .utils import make_uid


def make_title_block():
    uid = make_uid()
    block = {
        "@type": "title",
        "copyrightIcon": "ri-copyright-line",
        "hideContentType": True,
        "hideCreationDate": True,
        "hideDownloadButton": False,
        "hideModificationDate": True,
        "hidePublishingDate": True,
        "styles": {},
    }

    return [uid, block]


def make_summary_block():
    uid = make_uid()
    block = {
        "@type": "metadata",
        "data": {"id": "description", "widget": "description"},
    }
    return [uid, block]


def make_narrow_layout_block():
    uid = make_uid()
    block = {"@type": "layoutSettings", "layout_size": "narrow_view"}
    return [uid, block]


def make_folder_listing_block():
    uid = make_uid()
    block = {
        "@type": "listing",
        "block": uid,
        "headlineTag": "h2",
        "variation": "default",
        "query": [],
        "querystring": {
            "query": [
                {
                    "i": "portal_type",
                    "o": "plone.app.querystring.operation.selection.any",
                    "v": ["Folder"],
                },
                {
                    "i": "path",
                    "o": "plone.app.querystring.operation.string.relativePath",
                    "v": ".",
                },
                {
                    "i": "review_state",
                    "o": "plone.app.querystring.operation.selection.any",
                    "v": ["published"],
                },
            ],
            "depth": "1",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        },
    }

    return [uid, block]


def simple_slate_to_volto_blocks(slate_value):
    res = []
    for para in slate_value:
        block = {"@type": "slate", "value": [para]}
        res.append([make_uid(), block])

    return res


def make_obs_countries_header(countrycode):
    flaguid = make_uid()
    blocks = {}
    blocks[flaguid] = {
        "@type": "countryFlag",
        "country_name": countrycode.upper(),
        "show_flag": True,
        "show_dropdown": True,
        "show_name": True,
    }

    block = {
        "@type": "group",
        "as": "div",
        "data": {
            "blocks": blocks,
            "blocks_layout": {"items": [flaguid]},
        },
        "styles": {
            "size": "container_width",
            "style_name": "content-box-primary",
            "useAsPageHeader": True,
        },
    }

    return block


def make_vibriomap_block():
    uid = make_uid()
    block = {
        "@type": "maps",
        "align": "full",
        "dataprotection": {},
        "height": "100vh",
        "url": "/@@vibriomap-view-simple",
    }
    return [uid, block]


def make_events_archive_block():
    block = {
        "@type": "tabs_block",
        "data": {
            "assetPosition": "top",
            "blocks": {
                "2794742d-95ef-4a18-b98c-2c6bbdedbfee": {
                    "@type": "tab",
                    "assetPosition": "top",
                    "blocks": {
                        "0b52f5cd-8627-4e02-bee3-066665ee0446": {
                            "@type": "slate",
                            "plaintext": "",
                            "value": [{"children": [{"text": ""}], "type": "p"}],
                        },
                        "2d000c1b-a0af-4737-9831-2aef80b9b5d1": {
                            "@type": "listing",
                            "block": "2da320ed-d12d-4319-8419-6c443b94e9e2",
                            "headlineTag": "h2",
                            "itemModel": {
                                "@type": "item",
                                "callToAction": {"label": "Read more"},
                                "hasDate": False,
                                "hasDescription": True,
                                "hasEventDate": True,
                                "hasIcon": False,
                                "hasImage": False,
                                "hasLink": True,
                                "maxDescription": 2,
                                "maxTitle": 2,
                                "styles": {},
                                "titleOnImage": False,
                            },
                            "query": [],
                            "querystring": {
                                "depth": "1",
                                "query": [
                                    {
                                        "i": "portal_type",
                                        "o": "plone.app.querystring.operation.selection.any",
                                        "v": ["Event"],
                                    },
                                    {
                                        "i": "review_state",
                                        "o": "plone.app.querystring.operation.selection.any",
                                        "v": ["published"],
                                    },
                                    {
                                        "i": "end",
                                        "o": "plone.app.querystring.operation.date.afterToday",
                                        "v": "",
                                    },
                                ],
                                "sort_on": "start",
                                "sort_order": "ascending",
                                "sort_order_boolean": True,
                            },
                            "styles": {},
                            "variation": "eventCards",
                        },
                    },
                    "blocks_layout": {
                        "items": [
                            "2d000c1b-a0af-4737-9831-2aef80b9b5d1",
                            "0b52f5cd-8627-4e02-bee3-066665ee0446",
                        ]
                    },
                    "iconSize": "small",
                    "imageSize": "icon",
                    "title": "Upcoming events",
                },
                "ab1af12e-f321-47a9-a9e4-d9be24d3be88": {
                    "@type": "tab",
                    "assetPosition": "top",
                    "blocks": {
                        "0954b3b9-35c4-49ca-b90a-e38695c382d3": {
                            "@type": "listing",
                            "block": "2da320ed-d12d-4319-8419-6c443b94e9e2",
                            "headlineTag": "h2",
                            "itemModel": {
                                "@type": "item",
                                "callToAction": {"label": "Read more"},
                                "hasDate": False,
                                "hasDescription": True,
                                "hasEventDate": True,
                                "hasIcon": False,
                                "hasImage": False,
                                "hasLink": True,
                                "maxDescription": 2,
                                "maxTitle": 2,
                                "styles": {},
                                "titleOnImage": False,
                            },
                            "query": [],
                            "querystring": {
                                "depth": "1",
                                "query": [
                                    {
                                        "i": "portal_type",
                                        "o": "plone.app.querystring.operation.selection.any",
                                        "v": ["Event"],
                                    },
                                    {
                                        "i": "review_state",
                                        "o": "plone.app.querystring.operation.selection.any",
                                        "v": ["published"],
                                    },
                                    {
                                        "i": "end",
                                        "o": "plone.app.querystring.operation.date.beforeToday",
                                        "v": "",
                                    },
                                ],
                                "sort_on": "effective",
                                "sort_order": "descending",
                                "sort_order_boolean": True,
                            },
                            "styles": {},
                            "variation": "eventCards",
                        },
                        "d29a59fd-0071-45c8-8785-5e554780b06a": {
                            "@type": "slate",
                            "plaintext": "",
                            "value": [{"children": [{"text": ""}], "type": "p"}],
                        },
                    },
                    "blocks_layout": {
                        "items": [
                            "0954b3b9-35c4-49ca-b90a-e38695c382d3",
                            "d29a59fd-0071-45c8-8785-5e554780b06a",
                        ]
                    },
                    "iconSize": "small",
                    "imageSize": "icon",
                    "title": "Past events",
                },
            },
            "blocks_layout": {
                "items": [
                    "2794742d-95ef-4a18-b98c-2c6bbdedbfee",
                    "ab1af12e-f321-47a9-a9e4-d9be24d3be88",
                ]
            },
            "iconSize": "small",
            "imageSize": "icon",
        },
        "menuFluid": True,
        "menuPointing": True,
        "menuSecondary": True,
        "variation": "default",
        "verticalAlign": "flex-start",
    }

    return [make_uid(), block]
