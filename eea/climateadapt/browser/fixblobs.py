# # Zope imports
# from ZODB.POSException import POSKeyError
# from zope.component import queryUtility
# from Products.CMFCore.interfaces import IPropertiesTool
# from Products.CMFCore.interfaces import IFolderish

# # Plone imports
# from Products.Five import BrowserView
# from Products.Archetypes.Field import FileField
# from Products.Archetypes.interfaces import IBaseContent
# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
# from plone.namedfile.interfaces import INamedFile
# from plone.dexterity.content import DexterityContent


# only_urls = []
# all_broken_links = []


# def add_broken_link(url, creation, modification, reason):
#     """ To know what item is broken
#         when was created / last time modified
#         why is in this list: "sure" (for blobs found by classic script)
#                              "maybe" (for advanced check)

#         The links with maybe must be checked manually before deleting them.
#     """
#     global only_urls
#     if url not in only_urls:
#         global all_broken_links
#         all_broken_links.append(
#             {
#                 'url': url,
#                 'creation': creation,
#                 'modification': modification,
#                 'reason': reason
#             }
#         )
#         only_urls.append(url)


# def check_at_blobs(context):
#     """ Archetypes content checker.
#         Return True if purge needed
#     """

#     if IBaseContent.providedBy(context):

#         schema = context.Schema()
#         for field in schema.fields():
#             id = field.getName()
#             if isinstance(field, FileField):
#                 try:
#                     field.get_size(context)
#                 except POSKeyError:
#                     print(("Found damaged AT FileField %s on %s" % (
#                             id, context.absolute_url())))
#                     return True
#                 except SystemError:
#                     # retry on SystemError('error return without exception set',)
#                     try:
#                         field.get_size(context)
#                     except POSKeyError:
#                         print(("Found damaged AT FileField %s on %s" % (
#                                 id, context.absolute_url())))
#                         return True

#     return False


# def check_dexterity_blobs(context):
#     """ Check Dexterity content for damaged blob fields
#         Return True if purge needed
#     """

#     # Assume dexterity contennt inherits from Item
#     if isinstance(context, DexterityContent):

#         # Iterate through all Python object attributes
#         for key, value in list(context.__dict__.items()):
#             # Ignore non-contentish attributes to speed up us a bit
#             if not key.startswith("_"):
#                 if INamedFile.providedBy(value):
#                     try:
#                         value.getSize()
#                     except POSKeyError:
#                         print(("Found damaged Dexterity plone.app.NamedFile \
#                                 %s on %s" % (key, context.absolute_url())))

#                         add_broken_link(
#                             url=context.absolute_url(),
#                             creation=context.creation_date,
#                             modification=context.modification_date,
#                             reason="sure"
#                         )

#                         return True
#                     except SystemError:
#                         try:
#                             value.getSize()
#                         except POSKeyError:
#                             print(("Found damaged Dexterity plone.app.NamedFile \
#                                     %s on %s" % (key, context.absolute_url())))

#                             add_broken_link(
#                                 url=context.absolute_url(),
#                                 creation=context.creation_date,
#                                 modification=context.modification_date,
#                                 reason="sure"
#                             )

#                             return True
        
#     return False


# def fix_blobs(context, only_check=True):
#     """ Iterate through the object variables and see if they are blob fields
#         and if the field loading fails then poof

#         only_check = False if you really want to delete the objects
#     """

#     if check_at_blobs(context) or check_dexterity_blobs(context):
#         print(("Bad blobs found on %s" % context.absolute_url() + " -> deleting"))

#         add_broken_link(
#             url=context.absolute_url(),
#             creation=context.creation_date,
#             modification=context.modification_date,
#             reason="sure"
#         )

#         if only_check is False:
#             parent = context.aq_parent
#             parent.manage_delObjects([context.getId()])


# def fix_blobs_advanced(context, only_check=True):
#     """ Discover other bad objects which are not found by fix_blobs,
#         but returns the same No blob file error
#     """
#     try:
#         context.get_size()
#     except Exception:
#         print(("MAYBE: {0} -> deleting".format(context.absolute_url())))
#         add_broken_link(
#             url=context.absolute_url(),
#             creation=context.creation_date,
#             modification=context.modification_date,
#             reason="maybe"
#         )

#         if only_check is False:
#             try:
#                 parent = context.aq_parent
#                 parent.manage_delObjects([context.getId()])
#             except Exception:
#                 pass  # already deleted


# def recurse(tree, only_check=True):
#     """ Walk through all the content on a Plone site

#         only_check = False if you really want to delete the objects
#     """
#     for id, child in tree.contentItems():

#         fix_blobs(child, only_check=only_check)
#         fix_blobs_advanced(child, only_check=only_check)

#         if IFolderish.providedBy(child):
#             recurse(child, only_check=only_check)


# class FixBlobsOnlyCheck(BrowserView):
#     """ The same as FixBlobs but do not delete objects only list them

#         Also list broken links in page as table with details.
#     """
#     index = ViewPageTemplateFile("pt/fixblobs.pt")

#     def disable_integrity_check(self):
#         """ Content HTML may have references to this broken image - we cannot
#         fix that HTML but link integrity check will yell if we try to
#         delete the bad image.
#         """

#         ptool = queryUtility(IPropertiesTool)
#         props = getattr(ptool, 'site_properties', None)
#         self.old_check = props.getProperty(
#                 'enable_link_integrity_checks', False)
#         props.enable_link_integrity_checks = False

#     def enable_integrity_check(self):
#         """ """
#         ptool = queryUtility(IPropertiesTool)
#         props = getattr(ptool, 'site_properties', None)
#         props.enable_link_integrity_checks = self.old_check

#     def render(self):
#         print("Checking blobs")
#         portal = self.context
#         self.disable_integrity_check()
#         recurse(portal, only_check=True)
#         self.enable_integrity_check()
#         print("All done")
#         return self.index()

#     @property
#     def broken_links(self):
#         global all_broken_links
#         return all_broken_links

#     def __call__(self):
#         global all_broken_links
#         all_broken_links = []
#         global only_urls
#         only_urls = []
#         return self.render()


# class FixBlobs(BrowserView):
#     """ Clean up content with damaged BLOB files

#         Run it with: site/fix-blobs-imsure-delete

#         but before this:
#         Run site/fix-blobs-only-check to check broken items to be deleted
#             manually check each link with Reason: maybe
#     """
#     def disable_integrity_check(self):
#         """ Content HTML may have references to this broken image - we cannot
#             fix that HTML but link integrity check will yell if we try to
#             delete the bad image.
#         """

#         ptool = queryUtility(IPropertiesTool)
#         props = getattr(ptool, 'site_properties', None)
#         self.old_check = props.getProperty(
#                 'enable_link_integrity_checks', False)
#         props.enable_link_integrity_checks = False

#     def enable_integrity_check(self):
#         ptool = queryUtility(IPropertiesTool)
#         props = getattr(ptool, 'site_properties', None)
#         props.enable_link_integrity_checks = self.old_check

#     def render(self):
#         # plone = getMultiAdapter(
#         # (self.context, self.request), name="plone_portal_state")
#         print("Checking blobs")
#         portal = self.context
#         self.disable_integrity_check()
#         recurse(portal, only_check=False)
#         self.enable_integrity_check()
#         print("All done")
#         return "OK - check console for status messages"

#     def __call__(self):
#         self.render()
#         return "OK - check console for status messages"