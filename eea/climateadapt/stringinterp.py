""" Special filters for plone.stringinterp
"""

from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.utils import getToolByName
from Products.LDAPUserFolder.LDAPDelegate import filter_format
from plone.stringinterp.adapters import BaseSubstitution
from zope.component import adapts


class BaseLDAPLookupEmailSubstitution(BaseSubstitution):

    group = ""  # override this in subclasses

    def safe_call(self):
        acl = getToolByName(self.context, 'acl_users')
        ldap = acl['ldap-plugin']['acl_users']
        resp = ldap._delegate.search(
            base=ldap.groups_base, scope=2,
            filter=filter_format('(cn=%s)', [self.group]),
            attrs=['uniqueMember'])
        results = resp.get('results', [])
        member_dns = results[0]['uniqueMember']
        uids = [dn.split(',')[0].split('=')[1] for dn in member_dns]
        tpl = "".join("(uid=%s)" % uid for uid in uids)
        filter = "(|%s)" % tpl
        resp = ldap._delegate.search(
            base=ldap.users_base, scope=1,
            filter=filter, attrs=['mail'])
        results = resp.get('results', [])
        mails = [m['mail'][0] for m in results]
        return ", ".join(mails) or ""


class CCAReviewerEmailSubstitution(BaseLDAPLookupEmailSubstitution):
    adapts(IContentish)

    category = u'Local Roles'
    description = u'CCA Reviewers E-Mails'

    group = 'extranet-cca-reviewers'

