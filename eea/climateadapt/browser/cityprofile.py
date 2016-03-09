from plone.dexterity.browser.view import DefaultView
from plone.api import portal
from DateTime import DateTime

class CityProfileView(DefaultView):
    """
    """
    
    def formated_date(self, modifiedTime):
        
        return portal.get_localized_time(datetime=modifiedTime)
    
