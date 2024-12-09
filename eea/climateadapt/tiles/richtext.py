from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
# from collective.cover.tiles.richtext import IRichTextTile
from plone.supermodel import model
# from collective.cover.tiles.richtext import RichTextTile
from plone.tiles.tile import PersistentTile
from eea.climateadapt import CcaAdminMessageFactory
from zope import schema
from zope.interface import implementer


class IRichTextWithTitle(model.Schema):
    """
    """

    title = schema.TextLine(
        title=CcaAdminMessageFactory('Title'),
        required=False,
    )

    dont_strip = schema.Bool(
        title=CcaAdminMessageFactory("Don't sanitize HTML"),
        description=CcaAdminMessageFactory("Use with care!"),
        default=False,
    )

    title_level = schema.Choice(
        title=CcaAdminMessageFactory("Change header style."),
        default="h1",
        vocabulary="eea.climateadapt.rich_header_level",
    )


@implementer(IRichTextWithTitle)
class RichTextWithTitle(PersistentTile):
    """
    """

    index = ViewPageTemplateFile('pt/richtext_with_title.pt')
