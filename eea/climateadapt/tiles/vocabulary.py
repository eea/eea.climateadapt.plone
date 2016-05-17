from eea.climateadapt.vocabulary import catalog_based_vocabulary
from eea.climateadapt.vocabulary import generic_vocabulary
from zope.interface import alsoProvides
from zope.schema.interfaces import IVocabularyFactory


search_types_vocabulary = catalog_based_vocabulary('search_type')
alsoProvides(search_types_vocabulary, IVocabularyFactory)

element_types_vocabulary = catalog_based_vocabulary('elements')
alsoProvides(element_types_vocabulary, IVocabularyFactory)

special_tags_vocabulary = catalog_based_vocabulary('special_tags')
alsoProvides(special_tags_vocabulary, IVocabularyFactory)

_regions = ['Adriatic-Ionian', 'Alpine Space', 'Northern Periphery and Arctic',
           'Atlantic', 'Balkan-Mediterranean', 'Baltic Sea',
           'Central Europe', 'Danube', 'Mediterranean', 'North Sea',
           'North West Europe', 'South West Europe', 'Other regions']
regions_vocabulary = generic_vocabulary(_regions)
alsoProvides(regions_vocabulary, IVocabularyFactory)
