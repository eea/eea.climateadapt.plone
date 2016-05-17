from eea.climateadapt.vocabulary import generic_vocabulary
from zope.interface import alsoProvides
from zope.schema.interfaces import IVocabularyFactory


_climateimpacts = [
    ("FORESTFIRES", "Forest Fires"),
    ("EXTREMETEMP", "Extreme Temperatures"),
    ("WATERSCARCE", "Water Scarcity"),
    ("FLOODING", "Flooding"),
    ("SEALEVELRISE", "Sea Level Rise"),
    ("DROUGHT", "Droughts"),
    ("STORM", "Storms"),
    ("ICEANDSNOW", "Ice and Snow"),
]
aceitem_climateimpacts_vocabulary = generic_vocabulary(_climateimpacts)
alsoProvides(aceitem_climateimpacts_vocabulary, IVocabularyFactory)

_sectors = [    # this is the canonical
    ("AGRICULTURE", "Agriculture and Forest"),
    ("BIODIVERSITY", "Biodiversity"),
    ("COASTAL", "Coastal areas"),
    ("DISASTERRISKREDUCTION", "Disaster Risk Reduction"),
    ("FINANCIAL", "Financial"),
    ("HEALTH", "Health"),
    ("INFRASTRUCTURE", "Infrastructure"),
    ("URBAN", "Urban"),
    ("MARINE", "Marine and Fisheries"),
    ("TOURISM", "Tourism"),
    ("ENERGY", "Energy"),
    ("OTHER", "Other"),
    ("WATERMANAGEMENT", "Water management"),
]
aceitem_sectors_vocabulary = generic_vocabulary(_sectors)
alsoProvides(aceitem_sectors_vocabulary, IVocabularyFactory)

_status_of_adapt_signature = [
    ("", "Select"),
    ("ALREADYSIGNED", "Already Signed"),
    ("INPROCESSSIGNING", "In the process of signing"),
]
status_of_adapt_signature_vocabulary = generic_vocabulary(_status_of_adapt_signature)
alsoProvides(status_of_adapt_signature_vocabulary, IVocabularyFactory)


# TODO: merge with _sectors vocabulary. This cannot be really done now, the
# CityProfile is defined differently in the Java code, the relevant people
# would need to agree on this
_key_vulnerable_adapt_sector = [
    ("AGRI_AND_FOREST", "Agriculture and Forest"),
    ("COASTAL_AREAS", "Coastal areas"),
    ("DISASTER_RISK", "Disaster Risk Reduction"),
    ("FINANCIAL", "Financial"),
    ("HEALTH", "Health"),
    ("INFRASTRUCTURE", "Infrastructure"),
    ("MARINE_AND_FISH", "Marine and Fisheries"),
    ("TOURISM", "Tourism"),
    ("ENERGY", "Energy"),
    ("OTHER", "Other"),
    ("BIODIVERSITY", "Biodiversity"),
    ("WATER_MANAGEMENT", "Water Management"),
    ("URBAN", "Urban"),
]
key_vulnerable_adapt_sector_vocabulary = generic_vocabulary(_key_vulnerable_adapt_sector)
alsoProvides(key_vulnerable_adapt_sector_vocabulary, IVocabularyFactory)


_stage_implementation_cycle = [
    ("PREPARING_GROUND", "Preparing the ground"),
    ("ASSESSING_RISKS_VULNER", "Assessing risks and vulnerabilities"),
    ("IDENTIF_ADAPT_OPT", "Identifying adaptation options"),
    ("ASSESSING_ADAPT_OPT", "Assessing adaptation options"),
    ("IMPLEMENTATION", "Implementation"),
    ("MONIT_AND_EVAL", "Monitoring and evaluation"),
]
stage_implementation_cycle_vocabulary = generic_vocabulary(_stage_implementation_cycle)
alsoProvides(stage_implementation_cycle_vocabulary, IVocabularyFactory)


_already_devel_adapt_strategy = [
    ("", "Select"),
    ("YES_HAVE_ADAPT_STRAT", "Yes, we have an adaptation strategy"),
    ("NO_HAVE_ADAPT_STRAT", "No, we do not have an adaptation strategy but are currently developing one"),
    ("MAYORS_ADAPT_FIRST_EX", "No, Mayors Adapt is the first example of my city considering adaptation and we will develop an adaptation strategy"),
    ("INTEG_ADAPT_EXIST_REL", "We (will) integrate adaptation into existing relevant plans"),
]
already_devel_adapt_strategy_vocabulary = generic_vocabulary(_already_devel_adapt_strategy)
alsoProvides(already_devel_adapt_strategy_vocabulary, IVocabularyFactory)


# TODO: isn't this the same vocabulary as _elements
_elements_mentioned_your_cp = [
    ("EU_POLICY", "Sector Policies"),
    ("MEASUREACTION", "Adaptation Measures and Actions"),
    ("OBSERVATIONS", "Observations and Scenarios"),
    ("PLANSTRATEGY", "Adaptation Plans and Strategies"),
    ("VULNERABILITY", "Vulnerability Assessment"),
]

elements_mentioned_your_cp_vocabulary = generic_vocabulary(_elements_mentioned_your_cp)
alsoProvides(elements_mentioned_your_cp_vocabulary, IVocabularyFactory)

_covenant = [
    ("", "Select"),
    ("YES", "Yes"),
    ("NO", "No"),
]
covenant_vocabulary = generic_vocabulary(_covenant)
alsoProvides(covenant_vocabulary, IVocabularyFactory)
