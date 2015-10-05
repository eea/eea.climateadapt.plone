from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.cover.tiles.richtext import IRichTextTile
from collective.cover.tiles.richtext import RichTextTile
from eea.climateadapt import MessageFactory as _
from zope import schema
from zope.interface import implements


class IRichTextWithTitle(IRichTextTile):
    """
    """

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )


class RichTextWithTitle(RichTextTile):
    """
    """

    implements(IRichTextWithTitle)

    index = ViewPageTemplateFile('pt/richtext_with_title.pt')
