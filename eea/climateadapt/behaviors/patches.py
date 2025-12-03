from collective.volto.subsites.content.subsite import ISubsite
from plone.app.contenttypes.behaviors.leadimage import ILeadImageBehavior
from plone.app.contenttypes.behaviors.tableofcontents import ITableOfContents

# from plone.app.dexterity.behaviors.discussion import IAllowDiscussion
from plone.app.dexterity.behaviors.exclfromnav import IExcludeFromNavigation
from plone.app.dexterity.behaviors.metadata import IDublinCore
from plone.app.dexterity.behaviors.nextprevious import INextPreviousToggle
from plone.app.event.dx.behaviors import (
    IEventBasic,
    IEventContact,
    IEventLocation,
    IEventRecurrence,
)
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.versioningbehavior.behaviors import IVersionable
from zope.interface import alsoProvides
from collective.geolocationbehavior.geolocation import IGeolocatable

alsoProvides(IGeolocatable["geolocation"], ILanguageIndependentField)

alsoProvides(ISubsite["subsite_logo"], ILanguageIndependentField)
alsoProvides(ISubsite["subsite_css_class"], ILanguageIndependentField)
alsoProvides(ISubsite["subsite_social_links"], ILanguageIndependentField)

alsoProvides(ITableOfContents["table_of_contents"], ILanguageIndependentField)
alsoProvides(ILeadImageBehavior["image"], ILanguageIndependentField)

alsoProvides(INextPreviousToggle["nextPreviousEnabled"], ILanguageIndependentField)
alsoProvides(IVersionable["changeNote"], ILanguageIndependentField)

alsoProvides(IEventBasic["start"], ILanguageIndependentField)
alsoProvides(IEventBasic["end"], ILanguageIndependentField)
alsoProvides(IEventBasic["whole_day"], ILanguageIndependentField)
alsoProvides(IEventBasic["open_end"], ILanguageIndependentField)
alsoProvides(IEventBasic["sync_uid"], ILanguageIndependentField)

alsoProvides(IEventLocation["location"], ILanguageIndependentField)
alsoProvides(IEventRecurrence["recurrence"], ILanguageIndependentField)

alsoProvides(IDublinCore["subjects"], ILanguageIndependentField)
alsoProvides(IDublinCore["creators"], ILanguageIndependentField)
alsoProvides(IDublinCore["contributors"], ILanguageIndependentField)
alsoProvides(IDublinCore["rights"], ILanguageIndependentField)

alsoProvides(IEventContact["contact_name"], ILanguageIndependentField)
alsoProvides(IEventContact["contact_email"], ILanguageIndependentField)
alsoProvides(IEventContact["contact_phone"], ILanguageIndependentField)
alsoProvides(IEventContact["event_url"], ILanguageIndependentField)

# alsoProvides(IAllowDiscussion["allow_discussion"], ILanguageIndependentField)

alsoProvides(IExcludeFromNavigation["exclude_from_nav"], ILanguageIndependentField)
IExcludeFromNavigation["exclude_from_nav"].required = False

#
# alsoProvides(IEventBasic["timezone"], ILanguageIndependentField)


def apply_patch():
    pass  # nothing, we rely on side-effect
