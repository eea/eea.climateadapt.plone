# 2024-02-19 10:31:25 ERROR plone.dexterity.schema Error resolving behavior plone.leadimage
# 2024-02-19 10:31:25 WARNING plone.dexterity.schema No behavior registration found for behavior named: "plone.translatable" - trying fallback lookup..."
# 2024-02-19 10:31:25 ERROR plone.dexterity.schema Error resolving behavior plone.translatable
# 2024-02-19 10:31:25 WARNING plone.dexterity.schema No behavior registration found for behavior named: "kitconcept.seo" - trying fallback lookup..."
# 2024-02-19 10:31:25 ERROR plone.dexterity.schema Error resolving behavior kitconcept.seo
# 2024-02-19 10:31:25 WARNING plone.dexterity.schema No behavior registration found for behavior named: "plone.namefromtitle" - trying fallback lookup..."
# 2024-02-19 10:31:25 ERROR plone.dexterity.schema Error resolving behavior plone.namefromtitle
# 2024-02-19 10:31:25 WARNING plone.dexterity.schema No behavior registration found for behavior named: "plone.allowdiscussion" - trying fallback lookup..."
# 2024-02-19 10:31:25 ERROR plone.dexterity.schema Error resolving behavior plone.allowdiscussion
# 2024-02-19 10:31:25 WARNING plone.dexterity.schema No behavior registration found for behavior named: "plone.excludefromnavigation" - trying fallback lookup..."
# 2024-02-19 10:31:25 ERROR plone.dexterity.schema Error resolving behavior plone.excludefromnavigation
# 2024-02-19 10:31:25 WARNING plone.dexterity.schema No behavior registration found for behavior named: "plone.constraintypes" - trying fallback lookup..."
# 2024-02-19 10:31:25 ERROR plone.dexterity.schema Error resolving behavior plone.constraintypes
# 2024-02-19 10:31:25 WARNING plone.dexterity.schema No behavior registration found for behavior named: "plone.relateditems" - trying fallback lookup..."
# 2024-02-19 10:31:25 ERROR plone.dexterity.schema Error resolving behavior plone.relateditems
# 2024-02-19 10:31:25 WARNING plone.dexterity.schema No behavior registration found for behavior named: "plone.nextprevioustoggle" - trying fallback lookup..."
# 2024-02-19 10:31:25 ERROR plone.dexterity.schema Error resolving behavior plone.nextprevioustoggle
# 2024-02-19 10:31:25 WARNING plone.dexterity.schema No behavior registration found for behavior named: "plone.leadimage" - trying fallback lookup..."
# 2024-02-19 10:31:25 ERROR plone.dexterity.schema Error resolving behavior plone.leadimage
# 2024-02-19 10:31:25 WARNING plone.dexterity.schema No behavior registration found for behavior named: "plone.translatable" - trying fallback lookup..."
# 2024-02-19 10:31:25 ERROR plone.dexterity.schema Error resolving behavior plone.translatable
# 2024-02-19 10:31:25 WARNING plone.dexterity.schema No behavior registration found for behavior named: "kitconcept.seo" - trying fallback lookup..."

from zope.interface import Interface


class IMissingVoltoLeadImage(Interface):
    pass


class IMissingPloneTranslatable(Interface):
    pass


class IMissingKitconceptSeo(Interface):
    pass


class IMissingNextPreviousToggle(Interface):
    pass


class IMissingPloneRelatedItems(Interface):
    pass


class IMissingPloneConstrainTypes(Interface):
    pass


class IMissingPloneExcludeFromNavigation(Interface):
    pass


class IMissingPloneAllowDiscussion(Interface):
    pass


class IMissingPloneNameFromTitle(Interface):
    pass


class IMissingPloneDublinCore(Interface):
    pass
