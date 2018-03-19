from plone.api import portal
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.view import DefaultView
from plone.dexterity.interfaces import IDexterityFTI
from plone.z3cform.fieldsets.extensible import FormExtender
from zope.component import getUtility


class CityProfileView(DefaultView):
    """
    """

    def city_modified(self):
        return portal.get_localized_time(self.context.modified())

    def formated_date(self, modifiedTime):
        modif_date = portal.get_localized_time(datetime=modifiedTime)

        return modif_date

        # import datetime
        # return datetime.datetime.strptime(modif_date, '%d %B %Y').strftime('%d/%m/%y')

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

    def label_from_dropdown(self, fname):
        schema = getUtility(
            IDexterityFTI, name='eea.climateadapt.city_profile').lookupSchema()
        ftype = schema.get(fname)
        ftype = ftype.bind(self.context)
        vocab = ftype.vocabulary

        if getattr(self.context, fname):
            term = vocab.getTermByToken(getattr(self.context, fname))

            return term.title

    def html_to_text(self, html):
        portal_transform = portal.get_tool(name='portal_transforms')

        data = portal_transform.convertTo(
            'text/plain', html, mimetype='text/html'
        )

        data = data.getData().strip()

        return data

    def check_richtext(self, fname):
        if hasattr(fname, 'value'):
            if fname.value is None:
                return False
            html = fname.value.output
        else:
            html = fname.output

        text = self.html_to_text(html)

        if text in ['-', '']:
            return False

        return True

    def check_sections(self, number):
        sections = {
            '1': [self.context.additional_information_on_climate_impacts],
            '3': [self.context.planned_current_adaptation_actions_and_responses
                  ],
            '4': [self.context.title_of_the_action_event,
                  self.context.long_description,
                  self.context.picture,
                  self.context.picture_caption],
        }

        section = sections.get(number)

        if len(section) == 1:
            if section[0] in [None, '-', '']:
                return False

            return True
        else:
            for b in section:
                if hasattr(b, 'output'):
                    b = self.html_to_text(b.output)

                if b not in [None, '-', '']:
                    return True

        return False

    def linkify(self, text):
        portal_transform = portal.get_tool(name='portal_transforms')

        xx = portal_transform.convertTo('text/x-web-intelligent',
                                        text.encode('utf-8'),
                                        mimetype='text/html').getData()
        text = portal_transform.convertTo(
            'text/html', xx, mimetype='text/x-web-intelligent').getData()

        if not text:
            return

        return text


class CityProfileFormExtender(FormExtender):

    def update(self):
        try:
            self.move('IGeolocatable.geolocation', after='country')
            self.remove('city_background_information_about_the_city')
            self.remove('status_of_mayors_adapt_signature')
            self.remove('ICategorization.subjects')
            self.remove('ICategorization.language')
            self.remove('IPublication.effective')
            self.remove('IPublication.expires')
            self.remove('IOwnership.creators')
            self.remove('IOwnership.contributors')
            self.remove('IOwnership.rights')
            labels = ['label_schema_categorization', 'label_schema_dates', 'label_schema_ownership']
            self.form.groups = [group for group in self.form.groups if group.label not in labels]
        except Exception:   # registered too loosely
            pass
        # self.remove('signature_date')


class CityProfileAddForm(DefaultAddForm):
    """ Add Form for City profile
    """
