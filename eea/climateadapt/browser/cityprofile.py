from zope.component import getUtility
from plone.dexterity.browser.view import DefaultView
from plone.dexterity.interfaces import IDexterityFTI
from plone.api import portal


class CityProfileView(DefaultView):
    """
    """

    def formated_date(self, modifiedTime):

        return portal.get_localized_time(datetime=modifiedTime)

    def implementation_state_img_url(self):
        _map = {
            None: 'city_profile_state_1.png',
            'PREPARING_GROUND': 'city_profile_state_1.png',
            'ASSESSING_RISKS_VULNER': 'city_profile_state_2.png',
            'IDENTIF_ADAPT_OPT': 'city_profile_state_3.png',
            'ASSESSING_ADAPT_OPT': 'city_profile_state_4.png',
            'IMPLEMENTATION': 'city_profile_state_5.png',
            'MONIT_AND_EVAL': 'city_profile_state_6.png'
        }
        url = "{portal_url}/{resource_directory}/{filename}".format(
            portal_url=self.context.portal_url(),
            resource_directory='++resource++eea.climateadapt/img',
            filename=_map.get(self.context.stage_of_the_implementation_cycle)
        )
        return url

    def labels_from_choice(self, fname):
        schema = getUtility(
            IDexterityFTI, name='eea.climateadapt.city_profile').lookupSchema()
        f = schema.get(fname)
        ftype = f.value_type
        ftype = ftype.bind(self.context)
        vocab = ftype.vocabulary
        titles = []
        if getattr(self.context, fname):
            for token in getattr(self.context, fname):
                try:
                    term = vocab.getTermByToken(token)
                except LookupError:
                    continue
                titles.append(term.title)
        return titles
