""" plone.app.stringinterp helpers
"""

from eea.climateadapt.city_profile import ICityProfile
from plone.stringinterp.adapters import BaseSubstitution
from zope.component import adapts
from zope.interface import Interface


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


class cityprofile_register_email(BaseSubstitution):
    description = u"CityProfile registration email"
    category = 'CityProfile'

    adapts(Interface)

    def safe_call(self):
        return self.context.email


class cityprofile_register_name(BaseSubstitution):
    description = u"CityProfile registration name"
    category = 'CityProfile'

    adapts(Interface)

    def safe_call(self):
        return self.context.name
