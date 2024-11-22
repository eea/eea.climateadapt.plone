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
    'Black Sea Basin',
    'Central Europe',
    'Danube',
    'Mediterranean',
    'Mediterranean Sea Basin',
    'North Sea',
    'North West Europe',
    'Northern Periphery',
    'South West Europe',
    'Other Regions'
]

regions_vocabulary = generic_vocabulary(_regions)
alsoProvides(regions_vocabulary, IVocabularyFactory)


BIOREGIONS = {}

for line in [_f for _f in labels.split('\n') if _f is not None]:
    if 'TRANS_BIO' not in line:
        continue
    first, label = line.split('=')
    name = first.split('-lbl-')[1]
    BIOREGIONS[name] = label

bioregions_vocab_factory = generic_vocabulary(BIOREGIONS)
alsoProvides(bioregions_vocab_factory, IVocabularyFactory)
