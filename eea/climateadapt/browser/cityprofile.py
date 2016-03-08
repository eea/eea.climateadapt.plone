from plone.dexterity.browser.view import DefaultView
from plone.api import portal

class CityProfileView(DefaultView):
    """
    """
    
    def formated_date(self, v):
        return portal.get_localized_time(valoare parametru)
    
# definesti functie
# from plone.api import portal
# functia returneaza portal.get_localized_time(valoare parametru)