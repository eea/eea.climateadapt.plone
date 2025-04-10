tile_fields = ["title", "description", "tile_title", "footer", "alt_text"]

# TODO: this needs to be used again
cca_event_languages = {
    "English": "EN",
    "German": "DE",
    "French": "FR",
    "Spanish": "ES",
    "Italian": "IT",
    "Dutch": "NL",
    "Romanian": "RO",
    "Polish": "PL",
    "Bulgarian": "BG",
    "Slovak": "SK",
    "Slovenian": "SI",
}

source_richtext_types = [
    "eea.climateadapt.publicationreport",
    "eea.climateadapt.researchproject",
    "eea.climateadapt.mapgraphdataset",
    "eea.climateadapt.video",
]

# fallback, some fields are also defined in generated schemas
# (<InterfaceClass plone.dexterity.schema.generated.cca_0_Link>,
# 'remoteUrl',
# <zope.schema._bootstrapfields.TextLine object at 0x7f032249ac10>)
LANGUAGE_INDEPENDENT_FIELDS = [
    "c3s_identifier",
    "contact_email",
    "contact_name",
    "details_app_toolbox_url",
    "duration",
    "event_url",
    "funding_programme",
    "method",
    "other_contributor",
    "organisational_contact_information",
    "organisational_websites",
    "overview_app_toolbox_url",
    "partners_source_link",
    "remoteUrl",
    "storage_type",
    "sync_uid",
    "timezone",
    "template_layout",
    "event_language",
    # tibi
    "image",
    "id",
    "language",
]

IGNORE_FIELDS = ["acronym", "id", "language", "portal_type", "contentType"]

CCA_LANGUAGES = [
    "bg",
    "cs",
    "da",
    "el",
    "et",
    "fi",
    "ga",
    "hr",
    "hu",
    "lt",
    "lv",
    "mt",
    "nl",
    "pt",
    "sk",
    "sl",
    "sv",
]

# contenttype_language_independent_fields = {
#     "Folder": ["effective"],
#     "eea.climateadapt.video": ["effective"],
#     "Link": ["effective"],
#     "eea.climateadapt.c3sindicator": ["effective"],
#     "eea.climateadapt.researchproject": ["effective"],
#     "eea.climateadapt.tool": [
#         "spatial_values",
#         "storage_type",
#         "publication_date",
#         "effective",
#     ],
#     "eea.climateadapt.guidancedocument": [
#         "storage_type",
#         "spatial_values",
#         "effective",
#     ],
#     "EasyForm": ["showFields", "effective"],
#     "eea.climateadapt.adaptationoption": [
#         "implementation_type",
#         "effective",
#     ],
#     "eea.climateadapt.mapgraphdataset": [
#         "storage_type",
#         "spatial_values",
#         "effective",
#         "source",
#     ],
#     "Collection": ["sort_reversed", "query", "effective"],
#     "Document": ["table_of_contents", "effective"],
#     "News Item": [
#         "health_impacts",
#         "image",
#         "effective",
#         "include_in_observatory",
#         "subject",
#     ],
#     "eea.climateadapt.casestudy": [
#         "geolocation",
#         "implementation_type",
#         "spatial_values",
#         "effective",
#         "source",
#         "geochars",
#     ],
#     "eea.climateadapt.aceproject": [
#         "specialtagging",
#         "spatial_values",
#         "funding_programme",
#         "effective",
#         "source",
#     ],
#     "eea.climateadapt.indicator": [
#         "publication_date",
#         "storage_type",
#         "spatial_values",
#         "effective",
#     ],
#     "eea.climateadapt.informationportal": [
#         "spatial_values",
#         "storage_type",
#         "publication_date",
#         "effective",
#     ],
#     "eea.climateadapt.organisation": [
#         "storage_type",
#         "spatial_values",
#         "publication_date",
#         "effective",
#     ],
#     "eea.climateadapt.publicationreport": [
#         "storage_type",
#         "spatial_values",
#         "metadata",
#         "effective",
#     ],
#     "Event": [
#         "timezone",
#         "start",
#         "end",
#         "effective",
#         "event_url",
#         "health_impacts",
#         "contact_email",
#         "location",
#         "contact_name",
#         "effective",
#         "include_in_observatory",
#     ],
#     "cca-event": [
#         "timezone",
#         "start",
#         "end",
#         "effective",
#         "contact_email",
#         "contact_name",
#         "event_language",
#         "event_url",
#     ],
#     "File": ["file", "effective", "filename"],
#     "Image": ["image", "effective", "filename"],
#     "collective.cover.content": ["effective", "template_layout"],
# }
