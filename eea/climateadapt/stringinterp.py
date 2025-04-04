""" Special filters for plone.stringinterp
"""

# from Products.CMFCore.interfaces import IContentish
# from Products.CMFCore.utils import getToolByName
# from Products.LDAPUserFolder.LDAPDelegate import filter_format
# from plone.stringinterp.adapters import BaseSubstitution
# from zope.component import adapts
# import logging


# logger = logging.getLogger("eea.climateadapt.stringinterp")


# class LdapMailsForThematicExperts(BaseSubstitution):
#     adapts(IContentish)

#     category = 'CCA Thematic Experts'

#     def safe_call(self):
#         acl = getToolByName(self.context, 'acl_users')
#         ldap = acl['ldap-plugin']['acl_users']
#         resp = ldap._delegate.search(
#             base=ldap.groups_base, scope=2,
#             filter=filter_format('(cn=%s)', [self.group]),
#             attrs=['uniqueMember'])
#         results = resp.get('results', [])
#         if not results:
#             logger.warning("Couldn't find email for %s", self.context.Title())
#             return ""

#         member_dns = results[0]['uniqueMember']
#         if member_dns[0] == '' and len(member_dns) == 1:
#             logger.warning("Couldn't find emails for %s", self.group)
#             return ""

#         uids = [dn.split(',')[0].split('=')[1] for dn in member_dns]
#         tpl = "".join("(uid=%s)" % uid for uid in uids)
#         filter = "(|%s)" % tpl
#         resp = ldap._delegate.search(
#             base=ldap.users_base, scope=1,
#             filter=filter, attrs=['uid', 'mail'])
#         results = resp.get('results', [])

#         mt = getToolByName(self.context, 'portal_membership')
#         uids = [m['uid'][0] for m in results]
#         object_sectors = self.context.sectors

#         if len(uids) == 0:
#             logger.warning("Couldn't find email for the group %s", self.group)
#             return ""

#         for uid in uids:
#             member = mt.getMemberById(uid)
#             user_sectors = member.getProperty('thematic_sectors', '')

#             if user_sectors == '':
#                 continue
#             user_sectors = user_sectors.split(',')
#             user_has_sector = False
#             for user_sector in user_sectors:
#                 if user_sector in object_sectors:
#                     user_has_sector = True
#                     break
#             if user_has_sector is False:
#                 uids.remove(uid)
#         if len(uids) == 0:
#             logger.warning("There are no users with any of the following " +
#                            "sectors:  %s", ", ".join(object_sectors))
#             return ""

#         mails = [m['mail'][0] for m in results if m['uid'][0] in uids]
#         return ", ".join(mails) or ""


# class cca_thematicexperts(LdapMailsForThematicExperts):
#     group = 'extranet-cca-thematicexperts'
#     description = group + ' E-Mails'


# class BaseLDAPLookupEmailSubstitution(BaseSubstitution):
#     adapts(IContentish)

#     category = 'CCA Groups'

#     def safe_call(self):
#         acl = getToolByName(self.context, 'acl_users')
#         ldap = acl['ldap-plugin']['acl_users']
#         resp = ldap._delegate.search(
#             base=ldap.groups_base, scope=2,
#             filter=filter_format('(cn=%s)', [self.group]),
#             attrs=['uniqueMember'])
#         results = resp.get('results', [])
#         if not results:
#             logger.warning("Couldn't find email for %s", self.context.Title())
#             return ""

#         member_dns = results[0]['uniqueMember']
#         uids = [dn.split(',')[0].split('=')[1] for dn in member_dns]
#         tpl = "".join("(uid=%s)" % uid for uid in uids)
#         filter = "(|%s)" % tpl
#         resp = ldap._delegate.search(
#             base=ldap.users_base, scope=1,
#             filter=filter, attrs=['mail'])
#         results = resp.get('results', [])
#         mails = [m['mail'][0] for m in results]
#         return ", ".join(mails) or ""


# class cca_ma(BaseLDAPLookupEmailSubstitution):
#     group = 'extranet-cca-ma'
#     description = group + ' E-Mails'


# class cca_ma_contacts(BaseLDAPLookupEmailSubstitution):
#     group = 'extranet-cca-ma-contacts'
#     description = group + ' E-Mails'


# class cca_ma_managers(BaseLDAPLookupEmailSubstitution):
#     group = 'extranet-cca-ma-managers'
#     description = group + ' E-Mails'


# class cca_newsevents(BaseLDAPLookupEmailSubstitution):
#     group = 'extranet-cca-newsevents'
#     description = group + ' E-Mails'


# class cca_powerusers(BaseLDAPLookupEmailSubstitution):
#     group = 'extranet-cca-powerusers'
#     description = group + ' E-Mails'


# class cca_reviewers(BaseLDAPLookupEmailSubstitution):
#     group = 'extranet-cca-reviewers'
#     description = group + ' E-Mails'


# class cca_managers(BaseLDAPLookupEmailSubstitution):
#     group = 'extranet-cca-managers'
#     description = group + ' E-Mails'


# class cca_checkers(BaseLDAPLookupEmailSubstitution):
#     group = 'extranet-cca-checkers'
#     description = group + ' E-Mails'


# class cca_editors(BaseLDAPLookupEmailSubstitution):
#     group = 'extranet-cca-editors'
#     description = group + ' E-Mails'
