from zope.interface import alsoProvides
from zope.schema.interfaces import IVocabularyFactory

from eea.climateadapt.vocabulary import (KeywordsVocabulary,
                                         generic_vocabulary, labels)

SearchTypesVocabularyFactory = KeywordsVocabulary('search_type')
ElementsVocabularyFactory = KeywordsVocabulary('elements')

_regions = [
    'Adriatic-Ionian',
    'Alpine Space',
    'Atlantic Area',
    'Balkan-Mediterranean',
    'Baltic Sea',
    'Central Europe',
    'Danube',
    'Mediterranean',
    'North Sea',
    'North West Europe',
    'Northern Periphery',
    'South West Europe',
    'Other Regions'
]

regions_vocabulary = generic_vocabulary(_regions)
alsoProvides(regions_vocabulary, IVocabularyFactory)


BIOREGIONS = {}

for line in filter(None, labels.split('\n')):
    if 'TRANS_BIO' not in line:
        continue
    first, label = line.split('=')
    name = first.split('-lbl-')[1]
    BIOREGIONS[name] = label

bioregions_vocab_factory = generic_vocabulary(BIOREGIONS)
alsoProvides(bioregions_vocab_factory, IVocabularyFactory)
