# from Products.CMFPlone.utils import getToolByName
from eea.climateadapt.browser import AceViewApi
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.browser.view import DefaultView
from plone.dexterity.interfaces import IDexterityEditForm
from plone.z3cform import layout
from plone.z3cform.fieldsets.extensible import FormExtender
from zope.interface import classImplements
import re


class VideosView(DefaultView, AceViewApi):
    """ Default view for videos
    """
    type_label = u"Videos"

    def form_youtube_url(self):
        pattern = r"((?<=(v|V)/)|(?<=be/)|(?<=(\?|\&)v=)|(?<=embed/))([\w-]+)"
        match = re.search(pattern, self.context.youtube_url)
        if not match:
            return None
        video_id = match.group()
        url = "https://www.youtube.com/embed/%s" % video_id
        return url


class VideosEditForm(DefaultEditForm):
    """ Edit form for videos
    """


VideosEditView = layout.wrap_form(VideosEditForm)
classImplements(VideosEditView, IDexterityEditForm)


class VideosAddForm(DefaultAddForm):
    """ Add Form for videos
    """


class VideosFormExtender(FormExtender):
    def update(self):
        self.move('youtube_url', after='title')
        self.move('video_height', after='youtube_url')
        self.remove('ICategorization.subjects')
        self.remove('ICategorization.language')
        self.remove('IPublication.effective')
        self.remove('IPublication.expires')
        self.remove('IOwnership.creators')
        self.remove('IOwnership.contributors')
        self.remove('IOwnership.rights')
        labels = ['label_schema_dates', 'label_schema_ownership']
        self.form.groups = [group for group in self.form.groups if group.label not in labels]
