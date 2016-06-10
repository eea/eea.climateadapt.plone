"""
Various page overrides
"""

from plone.app.widgets.browser import vocabulary as vocab
from plone.dexterity.browser.add import DefaultAddView
from types import FunctionType
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory
import inspect


class VocabularyView(vocab.VocabularyView):
    """ Override the default getVocabulary because it doesn't work
    well with the add view
    """

    _vocabs = [
        ('eea.climateadapt.keywords', 'keywords'),
        ('eea.climateadapt.special_tags', 'special_tags'),
    ]

    def get_vocabulary(self):
        context = self.get_context()
        factory_name = self.request.get('name', None)
        field_name = self.request.get('field', None)

        if (factory_name, field_name) not in self._vocabs:
            return super(VocabularyView, self).get_vocabulary()

        factory = queryUtility(IVocabularyFactory, factory_name)
        if not factory:
            raise vocab.VocabLookupException(
                'No factory with name "%s" exists.' % factory_name)

        # This part is for backwards-compatibility with the first
        # generation of vocabularies created for plone.app.widgets,
        # which take the (unparsed) query as a parameter of the vocab
        # factory rather than as a separate search method.
        if type(factory) is FunctionType:
            factory_spec = inspect.getargspec(factory)
        else:
            factory_spec = inspect.getargspec(factory.__call__)
        query = vocab._parseJSON(self.request.get('query', ''))
        if query and 'query' in factory_spec.args:
            vocabulary = factory(context, query=query)
        else:
            # This is what is reached for non-legacy vocabularies.
            vocabulary = factory(context)

        return vocabulary


from Acquisition import aq_inner

class AddView(DefaultAddView):
    """ Add form page for case studies
    """

    def __init__(self, context, request, ti):
        self.context = context
        self.request = request

        if self.form is not None:

            if ti.klass == 'eea.climateadapt.acemeasure.CaseStudy':
                from eea.climateadapt.browser.casestudy import CaseStudyAddForm
                self.form = CaseStudyAddForm
            elif ti.klass == 'eea.climateadapt.acemeasure.AdaptationOption':
                from eea.climateadapt.browser.adaptationoption import \
                    AdaptationOptionAddForm
                self.form = AdaptationOptionAddForm

            self.form_instance = self.form(aq_inner(self.context), self.request)
            self.form_instance.__name__ = self.__name__

        self.ti = ti

        # Set portal_type name on newly created form instance
        if self.form_instance is not None \
           and not getattr(self.form_instance, 'portal_type', None):
            self.form_instance.portal_type = ti.getId()
