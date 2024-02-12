from .utils import make_uid


def make_title_block():
    uid = make_uid()
    block = {
        "@type": "title",
        "copyrightIcon": "ri-copyright-line",
        "hideContentType": True,
        "hideCreationDate": True,
        "hideDownloadButton": True,
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
