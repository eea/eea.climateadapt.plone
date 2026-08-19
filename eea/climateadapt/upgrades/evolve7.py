from plone import api


RELATED_TOOL_INDEXES = (
    "climate_impacts",
    "adaptation_support_cycle_step",
)


def reindex_related_tool_fields(context):
    """Populate the new indexes and metadata columns for existing tools."""
    catalog = api.portal.get_tool("portal_catalog")
    brains = catalog.unrestrictedSearchResults(
        portal_type="eea.climateadapt.extendedtool"
    )
    for brain in brains:
        brain.getObject().reindexObject(idxs=RELATED_TOOL_INDEXES)
