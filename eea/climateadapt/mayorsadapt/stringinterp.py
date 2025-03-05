""" plone.app.stringinterp helpers
"""

from eea.climateadapt.city_profile import ICityProfile
from plone.stringinterp.adapters import BaseSubstitution
from zope.component import adapts
from zope.interface import Interface


class cityprofile_contact_name(BaseSubstitution):
    description = "CityProfile contact name"
    category = 'CityProfile'

    adapts(ICityProfile)

    def safe_call(self):
        return getattr(self.context, 'name_and_surname_of_contact_person', '')


class cityprofile_contact_email(BaseSubstitution):
    description = "CityProfile contact email"
    category = 'CityProfile'

    adapts(ICityProfile)

    def safe_call(self):
        return getattr(self.context, 'e_mail_of_contact_person', '')


class cityprofile_existing_private_edit_link(BaseSubstitution):
    description = "CityProfile: Existing private edit link"
    category = 'CityProfile'

    adapts(ICityProfile)

    def safe_call(self):
        return self.context.get_private_edit_link()


class cityprofile_new_private_edit_link(BaseSubstitution):
    description = "CityProfile: New private edit link"
    category = 'CityProfile'

    adapts(ICityProfile)

    def safe_call(self):
        return self.context.get_private_edit_link()


class cityprofile_register_email(BaseSubstitution):
    description = "CityProfile registration email"
    category = 'CityProfile'

    adapts(Interface)

    def safe_call(self):
        return self.context.email


class cityprofile_register_name(BaseSubstitution):
    description = "CityProfile registration name"
    category = 'CityProfile'

    adapts(Interface)

    def safe_call(self):
        return self.context.name
