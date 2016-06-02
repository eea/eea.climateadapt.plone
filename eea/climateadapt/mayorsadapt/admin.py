from Products.Five.browser import BrowserView
from eea.climateadapt.city_profile import generate_secret
from eea.climateadapt.city_profile import send_token_mail
from zope.annotation.interfaces import IAnnotations
from zope.interface import Interface
from zope.interface import implements
from plone.api.portal import show_message
from plone.api.content import get_state


class ICityAdminView (Interface):
    """ City Profile Administrator Interface """


class CityAdminView (BrowserView):
    """ Custom view for the administration of city-profiles
        The process for resetting a profile token goes like this:
        - Select checkboxes
        - Press submit
        - Searches for the respective city profiles
        - Processes each city profile
            - Generates new token and sends email to respective owners
    """

    implements(ICityAdminView)

    def __call__(self):
        if 'submit' in self.request.form:
            for cityid in self.request.form['city']:
                for b in self.context.portal_catalog.searchResults(id=[cityid.lower()]):
                    cityobject = b.getObject()
                    newtokenid = generate_secret()
                    annot = IAnnotations(cityobject)
                    annot['eea.climateadapt.cityprofile_secret'] = newtokenid
                    send_token_mail(cityobject)

            show_message("Email(s) sent", request=self.request, type='info')

        cat = self.context.portal_catalog
        q = { 'portal_type': 'eea.climateadapt.city_profile' }
        self.res = [brain.getObject() for brain in cat.searchResults(**q)]

        return self.index()

    def get_status(self, city):
        try:
            return get_state(city)
        except Exception, e:
            return "Error: %s" % e
