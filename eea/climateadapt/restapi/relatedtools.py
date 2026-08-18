from plone import api
from plone.restapi.interfaces import IExpandableElement
from zope.component import adapter
from zope.interface import Interface, implementer

from eea.climateadapt.behaviors.extendedtool import IExtendedTool


RELATED_FIELDS = (
    "sectors",
    "climate_impacts",
    "adaptation_support_cycle_step",
)
NON_RELATIONSHIP_VALUES = {"NONSPECIFIC"}
PORTAL_TYPE = "eea.climateadapt.extendedtool"
MAX_RELATED_TOOLS = 3


def normalized_values(values):
    """Return meaningful taxonomy tokens as a set."""
    if not values:
        return set()
    if isinstance(values, str):
        values = [values]
    return {value for value in values if value and value not in NON_RELATIONSHIP_VALUES}


def dice_similarity(left, right):
    """Calculate the Sorensen-Dice similarity of two token sets."""
    if not left or not right:
        return 0.0
    return (2.0 * len(left & right)) / (len(left) + len(right))


def relationship(current, candidate):
    """Calculate relationship metadata using only the three taxonomies."""
    shared = {
        field: sorted(current[field] & candidate[field]) for field in RELATED_FIELDS
    }
    matching_dimensions = sum(bool(values) for values in shared.values())
    shared_values = sum(len(values) for values in shared.values())
    score = sum(
        dice_similarity(current[field], candidate[field]) for field in RELATED_FIELDS
    )
    return {
        "score": score,
        "matching_dimensions": matching_dimensions,
        "shared_values": shared_values,
        "shared": shared,
    }


@implementer(IExpandableElement)
@adapter(IExtendedTool, Interface)
class RelatedTools:
    """Related Extended Tools expander."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def endpoint_url(self):
        return f"{self.context.absolute_url()}/@relatedtools"

    def _current_taxonomies(self):
        return {
            field: normalized_values(getattr(self.context, field, None))
            for field in RELATED_FIELDS
        }

    def _catalog_candidates(self, current):
        portal = api.portal.get()
        language = self.context.Language()
        candidates = {}
        base_query = {
            "context": portal,
            "portal_type": PORTAL_TYPE,
            "review_state": "published",
            "Language": language,
        }

        for field in RELATED_FIELDS:
            values = current[field]
            if not values:
                continue
            query = {
                **base_query,
                field: {"query": list(values), "operator": "or"},
            }
            for brain in api.content.find(**query):
                if brain.getPath() != "/".join(self.context.getPhysicalPath()):
                    candidates[brain.getPath()] = brain

        return candidates.values()

    def _serialize_candidate(self, candidate):
        brain = candidate["brain"]
        obj = brain.getObject()
        return {
            "@id": brain.getURL(),
            "@type": brain.portal_type,
            "title": brain.Title,
            "description": brain.Description,
            "tool_provider": getattr(obj, "tool_provider", ""),
            "shared": candidate["shared"],
        }

    def _items(self):
        current = self._current_taxonomies()
        if not any(current.values()):
            return []

        related = []
        for brain in self._catalog_candidates(current):
            candidate = {
                field: normalized_values(getattr(brain, field, None))
                for field in RELATED_FIELDS
            }
            relation = relationship(current, candidate)
            if not relation["shared_values"]:
                continue
            related.append(
                {
                    "brain": brain,
                    "path": brain.getPath(),
                    **relation,
                }
            )

        related.sort(
            key=lambda item: (
                -item["score"],
                -item["matching_dimensions"],
                -item["shared_values"],
                item["path"],
            )
        )
        return [
            self._serialize_candidate(candidate)
            for candidate in related[:MAX_RELATED_TOOLS]
        ]

    def __call__(self, expand=False):
        items = self._items()
        return {
            "relatedtools": {
                "@id": self.endpoint_url,
                "items": items,
                "items_total": len(items),
            }
        }
