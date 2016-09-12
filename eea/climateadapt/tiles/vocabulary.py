from eea.climateadapt.vocabulary import KeywordsVocabulary
from eea.climateadapt.vocabulary import generic_vocabulary
from zope.interface import alsoProvides
from zope.schema.interfaces import IVocabularyFactory


SearchTypesVocabularyFactory = KeywordsVocabulary('search_type')
ElementsVocabularyFactory = KeywordsVocabulary('elements')

_regions = ['Adriatic-Ionian', 'Alpine Space', 'Northern Periphery and Arctic',
           'Atlantic', 'Balkan-Mediterranean', 'Baltic Sea',
           'Central Europe', 'Danube', 'Mediterranean', 'North Sea',
           'North West Europe', 'South West Europe', 'Other regions']
regions_vocabulary = generic_vocabulary(_regions)
alsoProvides(regions_vocabulary, IVocabularyFactory)
