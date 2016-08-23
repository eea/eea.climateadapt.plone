""" Special filters for plone.stringinterp
"""

from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.utils import getToolByName
from Products.LDAPUserFolder.LDAPDelegate import filter_format
from eea.climateadapt.city_profile import ICityProfile
from plone.stringinterp.adapters import BaseSubstitution
from zope.component import adapts
import logging


logger = logging.getLogger("eea.climateadapt.stringinterp")


class BaseLDAPLookupEmailSubstitution(BaseSubstitution):
    adapts(IContentish)

    category = u'CCA Groups'

    def safe_call(self):
        acl = getToolByName(self.context, 'acl_users')
        ldap = acl['ldap-plugin']['acl_users']
        resp = ldap._delegate.search(
            base=ldap.groups_base, scope=2,
            filter=filter_format('(cn=%s)', [self.group]),
            attrs=['uniqueMember'])
        results = resp.get('results', [])
        if not results:
            logger.warning("Couldn't find email for %s", self.context.Title())
            return ""

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


class cca_ma(BaseLDAPLookupEmailSubstitution):
    group = 'extranet-cca-ma'
    description = group + u' E-Mails'


class cca_ma_contacts(BaseLDAPLookupEmailSubstitution):
    group = 'extranet-cca-ma-contacts'
    description = group + u' E-Mails'


class cca_ma_managers(BaseLDAPLookupEmailSubstitution):
    group = 'extranet-cca-ma-managers'
    description = group + u' E-Mails'


class cca_newsevents(BaseLDAPLookupEmailSubstitution):
    group = 'extranet-cca-newsevents'
    description = group + u' E-Mails'


class cca_powerusers(BaseLDAPLookupEmailSubstitution):
    group = 'extranet-cca-powerusers'
    description = group + u' E-Mails'


class cca_reviewers(BaseLDAPLookupEmailSubstitution):
    group = 'extranet-cca-reviewers'
    description = group + u' E-Mails'


class cca_managers(BaseLDAPLookupEmailSubstitution):
    group = 'extranet-cca-managers'
    description = group + u' E-Mails'


class cca_checkers(BaseLDAPLookupEmailSubstitution):
    group = 'extranet-cca-checkers'
    description = group + u' E-Mails'


class cca_editors(BaseLDAPLookupEmailSubstitution):
    group = 'extranet-cca-editors'
    description = group + u' E-Mails'


class cityprofile_contact_name(BaseSubstitution):
    description = u"CityProfile contact name"
    category = 'CityProfile'

    adapts(ICityProfile)

    def safe_call(self):
        return getattr(self.context, 'name_and_surname_of_contact_person', '')


class cityprofile_contact_email(BaseSubstitution):
    description = u"CityProfile contact email"
    category = 'CityProfile'

    adapts(ICityProfile)

    def safe_call(self):
        return getattr(self.context, 'official_email', '')


class cityprofile_private_edit_link(BaseSubstitution):
    description = u"CityProfile private edit link"
    category = 'CityProfile'

    adapts(ICityProfile)

    def safe_call(self):
        return self.context.get_private_edit_link()
