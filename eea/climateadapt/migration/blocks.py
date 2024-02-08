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
