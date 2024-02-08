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
