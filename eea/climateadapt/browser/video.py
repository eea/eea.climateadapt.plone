import re

from eea.climateadapt.browser import AceViewApi
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.browser.view import DefaultView
from plone.dexterity.interfaces import IDexterityEditForm
from plone.z3cform import layout
from plone.z3cform.fieldsets.extensible import FormExtender
from zope.interface import classImplements

YOUTUBE_RE = r"((?<=(v|V)/)|(?<=be/)|(?<=(\?|\&)v=)|(?<=embed/))([\w-]+)"


class VideoView(DefaultView, AceViewApi):
    """ Default view for video

    Warning: the embed code is not sanitized.
    """
    type_label = "Video"

    def embed_url(self):
        # first, test to see if it could be a youtube video

        url = getattr(self.context, 'embed_url', None)

        if not url:
            return

        strategies = ['_youtube_url']

        for name in strategies:
            method = getattr(self, name)
            url = method()

            if url:
                return url

    def _youtube_url(self):
        match = re.search(YOUTUBE_RE, self.context.embed_url)

        if not match:
            return None

        video_id = match.group()
        url = "https://www.youtube.com/embed/%s" % video_id

        return url


class VideoEditForm(DefaultEditForm):
    """ Edit form for video
    """


VideoEditView = layout.wrap_form(VideoEditForm)
classImplements(VideoEditView, IDexterityEditForm)


class VideoAddForm(DefaultAddForm):
    """ Add Form for videos
    """


# VideoAddView = layout.wrap_form(VideoAddForm)
# classImplements(VideoAddView, IAddForm)


class VideoFormExtender(FormExtender):

    def update(self):
        self.move('embed_url', after='title')
        self.move('video_height', after='embed_url')
        self.move('related_documents_presentations', after='embed_url')
        self.move('IRelatedItems.relatedItems', after='comments')

        self.remove('ICategorization.subjects')
        self.remove('ICategorization.language')
        self.remove('IPublication.effective')
        self.remove('IPublication.expires')
        self.remove('IOwnership.creators')
        self.remove('IOwnership.contributors')
        self.remove('IOwnership.rights')

        self.remove('IBlocks.blocks')
        self.remove('IBlocks.blocks_layout')

        labels = ['label_schema_dates',
                  'label_schema_ownership', 'Layout', 'Settings']
        self.form.groups = [
            group for group in self.form.groups

            if group.label not in labels
        ]
