from eea.climateadapt import CcaAdminMessageFactory as _
from plone import schema
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


@provider(IFormFieldProvider)
class ISEOFields(model.Schema):
    """ """

    model.fieldset(
        "seofields",
        label=_("SEO"),
        fields=("seo_title", "seo_description", "seo_robots"),
    )

    seo_title = schema.TextLine(
        title=_("SEO Title"),
        description=_(
            "seo_title_help",
            default=(
                "Used in the web page 'head' section title and "
                "browser tab instead of the default title."
            ),
        ),
        required=False,
    )

    seo_description = schema.Text(
        title=_("SEO Description"),
        description=_(
            "seo_description_help",
            default=(
                "Used as meta description field in the 'head' section "
                "of a page instead of the default description."
            ),
        ),
        required=False,
    )

    seo_robots = schema.Choice(
        title=_("Metatag Robots"),
        description=_(
            "seo_robots_help",
            default=(
                "Select options that hint search engines how "
                "to treat this content. Typically listings are to "
                "navigate the site, but add little to no value in its "
                "own and should be set to 'noindex, follow'. In some "
                "cases you want a listing to be indexed. E.g. when "
                "publishing a Top 10 recipes list with extra content "
                "above and below the list, in which case you would use "
                "'index,follow'."
            ),
        ),
        # vocabulary="seofields.robots",
        vocabulary=SimpleVocabulary([
            SimpleTerm(value='noindex, nofollow', title=u'noindex, nofollow'),
            SimpleTerm(value='noindex', title=u'noindex'),
            SimpleTerm(value='nofollow', title=u'nofollow'),
        ]),
        required=False,
    )


@implementer(ISEOFields)
@adapter(IDexterityContent)
class SEOFields:
    def __init__(self, context):
        self.context = context

    @property
    def seo_title(self):
        if hasattr(self.context, "seo_title"):
            return self.context.seo_title
        return None

    @seo_title.setter
    def seo_title(self, value):
        self.context.seo_title = value

    @property
    def seo_description(self):
        if hasattr(self.context, "seo_description"):
            return self.context.seo_description
        return None

    @seo_description.setter
    def seo_description(self, value):
        self.context.seo_description = value

    @property
    def seo_robots(self):
        if hasattr(self.context, "seo_robots"):
            return self.context.seo_robots
        return None

    @seo_robots.setter
    def seo_robots(self, value):
        self.context.seo_robots = value
