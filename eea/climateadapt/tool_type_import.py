"""Import Extended Tool category assignments from an ODS spreadsheet."""

import logging
import xml.etree.ElementTree as ET
import zipfile

import transaction
from plone import api

from eea.climateadapt.tool_import import parse_ods_rows
from eea.climateadapt.vocabulary import _tool_types


logger = logging.getLogger("eea.climateadapt.importer.tool_types")

DEFAULT_TARGET_PATH = "/cca/en/metadata/tools"
PORTAL_TYPE = "eea.climateadapt.extendedtool"


class ToolTypeAssignmentError(ValueError):
    """Raised when the assignment spreadsheet is invalid."""


def normalize_tool_type_value(value):
    """Normalize spreadsheet text for reliable matching."""
    return " ".join((value or "").replace("\xa0", " ").split()).casefold()


TOOL_TYPE_LABEL_TO_TOKEN = {
    normalize_tool_type_value(str(label)): token for token, label in _tool_types
}
TOOL_TYPE_TOKEN_TO_LABEL = {token: str(label) for token, label in _tool_types}


def normalize_tool_id(value):
    """Return Tool IDs in the canonical ``#123`` form."""
    value = " ".join(str(value or "").replace("\xa0", " ").split())
    if value.endswith(".0") and value[:-2].isdigit():
        value = value[:-2]
    value = value.lstrip("#").strip()
    return f"#{value}" if value else ""


def _normalized_header(value):
    return normalize_tool_type_value(value)


def parse_assignment_rows(rows):
    """Parse and validate rows from the ``Tool icons`` ODS sheet."""
    required_headers = {
        "tool id": "external_id",
        "tool name": "name",
        "tool type (category)": "category",
    }

    header_index = None
    columns = {}
    for row_index, row in enumerate(rows):
        normalized = [_normalized_header(cell) for cell in row]
        if all(header in normalized for header in required_headers):
            header_index = row_index
            columns = {
                field: normalized.index(header)
                for header, field in required_headers.items()
            }
            break

    if header_index is None:
        expected = ", ".join(required_headers)
        raise ToolTypeAssignmentError(
            f"Could not find the assignment header row. Expected: {expected}"
        )

    assignments = {}
    errors = []
    for row_number, row in enumerate(rows[header_index + 1 :], header_index + 2):

        def value(field):
            index = columns[field]
            return row[index].strip() if index < len(row) and row[index] else ""

        external_id = normalize_tool_id(value("external_id"))
        name = value("name")
        category = value("category")

        if not any((external_id, name, category)):
            continue
        if not external_id:
            errors.append(f"row {row_number}: missing Tool ID")
            continue
        if external_id in assignments:
            errors.append(f"row {row_number}: duplicate Tool ID {external_id}")
            continue

        tool_type = TOOL_TYPE_LABEL_TO_TOKEN.get(normalize_tool_type_value(category))
        if not tool_type:
            errors.append(
                f"row {row_number} ({external_id}): unknown category {category!r}"
            )
            continue

        assignments[external_id] = {
            "external_id": external_id,
            "name": name,
            "tool_type": tool_type,
            "category": TOOL_TYPE_TOKEN_TO_LABEL[tool_type],
        }

    if errors:
        raise ToolTypeAssignmentError("\n".join(errors))
    if not assignments:
        raise ToolTypeAssignmentError("The assignment spreadsheet contains no tools")

    return assignments


def parse_assignment_ods(file_or_path):
    """Parse assignments from an ODS path, bytes, or uploaded file."""
    try:
        rows = parse_ods_rows(file_or_path)
    except (KeyError, OSError, ET.ParseError, zipfile.BadZipFile) as error:
        message = f"Could not read the ODS file: {error}"
        raise ToolTypeAssignmentError(message) from error
    return parse_assignment_rows(rows)


class ToolTypeImporter:
    """Apply validated tool-type assignments to existing Extended Tools."""

    def resolve_container(self, site, container=None):
        if container is not None and not isinstance(container, str):
            try:
                from Products.CMFPlone.interfaces import IPloneSiteRoot

                if IPloneSiteRoot.providedBy(container):
                    container = None
                else:
                    return container
            except ImportError:
                return container

        target_path = container or DEFAULT_TARGET_PATH
        resolved = api.content.get(path=target_path)
        if not resolved and hasattr(site, "unrestrictedTraverse"):
            relative_path = target_path.lstrip("/")
            portal_id = getattr(site, "getId", lambda: "")()
            if portal_id and relative_path.startswith(f"{portal_id}/"):
                relative_path = relative_path[len(portal_id) + 1 :]
            resolved = site.unrestrictedTraverse(relative_path, None)
        if not resolved:
            raise RuntimeError(f"Folder {target_path} not found")
        return resolved

    def import_assignments(self, site, assignments, dry_run=True, container=None):
        """Update only ``tool_type`` on tools matched by ``external_id``."""
        container = self.resolve_container(site, container)
        existing = {}
        duplicate_ids = []
        for _item_id, obj in container.objectItems():
            if getattr(obj, "portal_type", None) != PORTAL_TYPE:
                continue
            external_id = normalize_tool_id(getattr(obj, "external_id", ""))
            if not external_id:
                continue
            if external_id in existing:
                duplicate_ids.append(external_id)
            existing[external_id] = obj

        if duplicate_ids:
            duplicate_ids = ", ".join(sorted(set(duplicate_ids)))
            raise ToolTypeAssignmentError(
                f"Duplicate Extended Tool external IDs in the target folder: "
                f"{duplicate_ids}"
            )

        missing_ids = [
            external_id for external_id in assignments if external_id not in existing
        ]
        if missing_ids and not dry_run:
            missing = ", ".join(missing_ids)
            raise ToolTypeAssignmentError(
                "No changes were made because assignment Tool IDs were not found: "
                f"{missing}. Run without --commit to inspect the complete report."
            )

        results = []
        for external_id, assignment in assignments.items():
            obj = existing.get(external_id)
            if obj is None:
                results.append({**assignment, "status": "NOT_FOUND", "url": ""})
                continue

            current = getattr(obj, "tool_type", None)
            if current == assignment["tool_type"]:
                status = "UNCHANGED"
            elif dry_run:
                status = "WOULD_UPDATE"
            else:
                obj.tool_type = assignment["tool_type"]
                obj._p_changed = True
                obj.reindexObject()
                status = "UPDATED"

            actual_name = obj.Title()
            if assignment["name"] and actual_name != assignment["name"]:
                logger.warning(
                    "Tool title differs for %s: spreadsheet=%r, Plone=%r",
                    external_id,
                    assignment["name"],
                    actual_name,
                )

            results.append(
                {
                    **assignment,
                    "status": status,
                    "url": obj.absolute_url(),
                    "actual_name": actual_name,
                }
            )

        if not dry_run:
            transaction.commit()

        return results

    def run_web_import(self, file_upload, context=None):
        """Parse an uploaded ODS file and apply its assignments."""
        assignments = parse_assignment_ods(file_upload)
        site = api.portal.get()
        return self.import_assignments(
            site,
            assignments,
            dry_run=False,
            container=context,
        )
