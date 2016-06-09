import time
from datetime import date, timedelta
import tokenlib
from tokenlib.errors import ExpiredTokenError
from Products.Five.browser import BrowserView
from zope.annotation.interfaces import IAnnotations as ann


class TokenCheckView(BrowserView):
    def __call__(self):
        brains = catalog_search(self)

        for city in brains:
            city = city.getObject()

            if has_token(city):
                diff = time_difference(city)
                if diff <= 7:
                    if(diff) == 0:
                        """ Send mail saying that the period expired to mayor
                            and administrator
                        """
                        pass
                    """ Send mail informing he has 1 week left
                    """
                    pass

                print city.Title()
            else:
                pass

        return self.index()


def catalog_search(self):
    cat = self.context.portal_catalog

    q = {
        'portal_type': 'eea.climateadapt.city_profile'
    }

    brains = cat.searchResults(**q)

    return brains


def has_token(city):
    if ann(city).get('eea.climateadapt.cityprofile_token_expires'):
        return True
    else:
        return False


def time_difference(city):
    time_left = get_time_left(city)
    time_now = date.today()

    time_delta = (time_left - time_now).days

    return time_delta


def get_time_left(city):
    time_left = ann(city).get('eea.climateadapt.cityprofile_token_expires')

    return time_left
