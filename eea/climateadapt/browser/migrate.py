import csv
import io
import json
import logging
import re
from copy import deepcopy
from datetime import date, datetime, timedelta

import pycountry
import transaction
from eea.climateadapt.interfaces import ICCACountry, ICCACountry2025
from eea.climateadapt.translation.utils import get_site_languages
from eea.climateadapt.vocabulary import (
    SUBNATIONAL_REGIONS,
    _climateimpacts,
    _sectors,
    _temporality_of_data_tool,
    _type_of_outputs_tool,
    european_countries,
)
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes

import logging
import csv
import io
import json
from datetime import datetime, timedelta
import pycountry
import re
import json

import transaction
from plone import api
from plone.app.textfield.value import RichTextValue
from plone.base.interfaces import ILanguage
from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.blocks import visit_blocks
from plone.restapi.deserializer.utils import path2uid
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.interface import alsoProvides, noLongerProvides
from zope.lifecycleevent import modified

logger = logging.getLogger("eea.climateadapt")


class MigrateAbsoluteURLs(BrowserView):
    """Migrate absolute URLs to resolveuid"""

    fields = [
        "url",
        "href",
        "provider_url",
        "link",
        "getRemoteUrl",
        "attachedImage",
        "attachedimage",
        "getPath",
        "getURL",
        "preview_image",
        "@id",
    ]
    count = 0

    def fix_url(self, block):
        if isinstance(block, dict):  # If the current data is a dictionary
            for key, value in block.items():
                if key in self.fields:  # Check for the 'url' key with the target value
                    if value and isinstance(value, str):
                        cleaned_url = clean_url(value)

                        if cleaned_url != value:
                            block[key] = path2uid(
                                context=self.context, link=cleaned_url
                            )
                            self.count += 1
                else:
                    self.fix_url(value)  # Recursively check the value

        elif isinstance(block, list):  # If the current data is a list
            for item in block:
                self.fix_url(item)

    def migrate(self):
        """Migrate absolute URLs to resolveuid"""
        query = {
            "context": self.context,
            "object_provides": "plone.restapi.behaviors.IBlocks",
        }

        # Get the request object
        request = self.request

        # Read the 'days' parameter from the request
        days = request.get("days", None)

        # Convert 'days' to an integer if it is provided
        if days is not None:
            try:
                days = int(days)
            except ValueError:
                # Handle the case where 'days' is not a valid integer
                days = None

        if days is not None:
            # Calculate the date `days` ago from today
            date = datetime.now() - timedelta(days=days)

            # Add the modified filter to the query
            query["modified"] = {"query": date, "range": "min"}

        brains = api.content.find(**query)

        total = len(brains)
        for idx, brain in enumerate(brains):
            obj = brain.getObject()
            # if obj.title == "Discover the key services, thematic features and tools of Climate-ADAPT":
            #     import pdb; pdb.set_trace()
            blocks = getattr(obj, "blocks", {})
            # blocks_orig = copy.deepcopy(blocks)

            if "localhost" in str(
                blocks
            ) or "https://climate-adapt.eea.europa.eu" in str(blocks):
                for block in visit_blocks(obj, blocks):
                    self.fix_url(block)

                try:
                    modified(obj)
                except Exception as e:
                    logger.error("Failed to update %s: %s", brain.getURL(), e)

            if idx % 100 == 0:
                transaction.commit()
                logger.info("Progress %s of %s. Migrated %s", idx, total, self.count)

        return self.count

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        count = self.migrate()
        IStatusMessage(self.request).addStatusMessage(
            "Migrated {} absolute URLs!".format(count)
        )
        return self.request.response.redirect(self.context.absolute_url())


class CountryMapInterface2025(BrowserView):
    """Migrate absolute URLs to resolveuid"""

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        portal_catalog = api.portal.get_tool("portal_catalog")
        languages = get_site_languages()
        for language in languages:
            logger.info(f"LANGUAGE %s", language)
            brains = portal_catalog.queryCatalog(
                {
                    "portal_type": "Folder",
                    "path": "/cca/{}/countries-regions/countries".format(language),
                }
            )
            for brain in brains:
                obj = brain.getObject()

                if ICCACountry.providedBy(obj):
                    noLongerProvides(obj, ICCACountry)
                    obj._p_changed = True

                if not ICCACountry2025.providedBy(obj):
                    alsoProvides(obj, ICCACountry2025)
                    obj._p_changed = True

                if obj._p_changed:
                    obj.reindexObject()
                    # transaction.commit()
                    logger.info(f"Interface update %s", brain.getURL())
        logger.info(f"Country profile interface check done")
        return "done"


class ArchiveItems294148(BrowserView):
    """#294148 Research and Knowledge Projects and Reports and Publications"""

    def list(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        portal_catalog = api.portal.get_tool("portal_catalog")
        languages = get_site_languages()

        # import pdb
        # pdb.set_trace()
        response = []
        filterPortalTypes = []
        if self.request.form.get("publicationreport", None):
            filterPortalTypes.append("eea.climateadapt.publicationreport")
        if self.request.form.get("aceproject", None):
            filterPortalTypes.append("eea.climateadapt.aceproject")

        if len(filterPortalTypes) == 0:
            filterPortalTypes.append("eea.climateadapt.notypeselected")

        for language in languages:
            # if language not in ['en']:
            #     continue
            logger.info(f"ArchiveItems294148 LANGUAGE %s", language)
            brains = portal_catalog(
                **{
                    "portal_type": filterPortalTypes,
                    "review_state": "published",
                    # "review_state": "archived",
                    "path": "/cca/{}/".format(language),
                }
            )
            itemNr = 1
            nrToArchive = 0
            for brain in brains:
                obj = brain.getObject()
                yearCreated = (
                    brain.created.year() if getattr(brain, "created", None) else None
                )
                yearPublication = (
                    obj.publication_date.year if obj.publication_date else None
                )

                toArchive = "N"
                if yearPublication and yearPublication < 2016:
                    nrToArchive += 1
                    toArchive = "Y"
                # elif yearCreated and yearCreated < 2016:
                #     nrToArchive += 1
                #     toArchive = 'Y'

                # if toArchive and self.request.form.get("doarchive", None):
                #     import pdb
                #     pdb.set_trace()
                if (
                    toArchive == "Y"
                    and self.request.form.get("publicationreport", None)
                    and self.request.form.get("doarchive", None)
                ):
                    api.content.transition(obj, "archive")
                    if nrToArchive % 100 == 0:
                        transaction.commit()
                response.append(
                    {
                        "itemNr": itemNr,
                        "nrToArchive": nrToArchive if toArchive == "Y" else "",
                        "toArchive": toArchive,
                        "title": obj.title,
                        "url": brain.getURL(),
                        "created": yearCreated,
                        "publication_date": yearPublication,
                    }
                )
                itemNr += 1
        transaction.commit()
        logger.info(f"ArchiveItems294148 check done")
        return response


def is_mission_reporting_question_folder(obj):
    """Return True for reporting question folders such as Q3.1.1.16."""
    title = getattr(obj, "title", "") or ""
    return re.match(r"^Q\d", title) is not None


class HideMissionSignatoryReportingFolders(BrowserView):
    """Exclude Mission Signatory Reporting folders from navigation."""

    signatory_reporting_path_template = (
        "{language}/eu-policy/eu-adaptation-policy/"
        "eu-mission-on-adaptation/signatory-reporting"
    )

    def should_change(self):
        value = self.request.form.get("change", "")
        return value.lower() in ("1", "true", "yes", "on")

    def get_language(self):
        language = self.request.form.get("language", "en").strip().lower()
        if not re.match(r"^[a-z]{2}$", language):
            raise ValueError("language must be a two-letter code")
        return language

    def get_signatory_reporting_path(self, language):
        return self.signatory_reporting_path_template.format(language=language)

    def get_root(self, language):
        portal = api.portal.get()
        path = self.get_signatory_reporting_path(language)
        return portal.unrestrictedTraverse(path, None)

    def get_brains(self, root):
        if root is None:
            return []

        catalog = api.portal.get_tool("portal_catalog")
        root_path = "/".join(root.getPhysicalPath())
        return catalog.unrestrictedSearchResults(
            path={"query": root_path},
            portal_type="Folder",
        )

    def result(self):
        if hasattr(self, "_result"):
            return self._result

        alsoProvides(self.request, IDisableCSRFProtection)

        change = self.should_change()
        language = self.get_language()
        signatory_reporting_path = self.get_signatory_reporting_path(language)
        root = self.get_root(language)

        if root is None:
            self._result = {
                "change": change,
                "language": language,
                "root_found": False,
                "path": signatory_reporting_path,
                "found": 0,
                "upgraded": 0,
                "already_excluded": 0,
            }
            logger.warning(
                "Signatory Reporting root not found at %s",
                signatory_reporting_path,
            )
            return self._result

        root_path = "/".join(root.getPhysicalPath())
        brains = [
            brain for brain in self.get_brains(root) if brain.getPath() != root_path
        ]
        folders = []
        for brain in brains:
            folder = brain.getObject()
            if is_mission_reporting_question_folder(folder):
                folders.append(folder)
        found = len(folders)
        upgraded = 0
        already_excluded = 0

        logger.info(
            "HideMissionSignatoryReportingFolders found %s question folders "
            "under %s. language=%s change=%s",
            found,
            root.absolute_url(),
            language,
            change,
        )

        for idx, folder in enumerate(folders, start=1):
            has_exclude_from_nav = getattr(folder, "exclude_from_nav", False)
            has_seo_noindex = getattr(folder, "seo_noindex", False)

            if has_exclude_from_nav and has_seo_noindex:
                already_excluded += 1
                continue

            if change:
                folder.exclude_from_nav = True
                folder.seo_noindex = True
                folder.reindexObject(idxs=["exclude_from_nav", "seo_noindex"])

                if idx % 100 == 0:
                    transaction.savepoint()

            upgraded += 1

        if change:
            transaction.commit()

        self._result = {
            "change": change,
            "language": language,
            "root_found": True,
            "path": "/".join(root.getPhysicalPath()),
            "url": root.absolute_url(),
            "found": found,
            "upgraded": upgraded,
            "already_excluded": already_excluded,
        }

        logger.info(
            "HideMissionSignatoryReportingFolders found=%s upgraded=%s "
            "already_excluded=%s language=%s change=%s",
            found,
            upgraded,
            already_excluded,
            language,
            change,
        )
        return self._result


class MigrateIndicatorVisualizations(BrowserView):
    """Move old Indicator map/graphs values to the visualizations field."""

    path_template = "{language}"
    portal_type = "eea.climateadapt.indicator"

    def should_change(self):
        value = self.request.form.get("change", "")
        return value.lower() in ("1", "true", "yes", "on")

    def get_language(self):
        language = self.request.form.get("language", "en").strip().lower()
        if not re.match(r"^[a-z]{2}$", language):
            raise ValueError("language must be a two-letter code")
        return language

    def get_path(self, language):
        return self.path_template.format(language=language)

    def get_root(self, language):
        portal = api.portal.get()
        path = self.get_path(language)
        return portal.unrestrictedTraverse(path, None)

    def get_brains(self, root):
        if root is None:
            return []

        catalog = api.portal.get_tool("portal_catalog")
        root_path = "/".join(root.getPhysicalPath())
        return catalog.unrestrictedSearchResults(
            path={"query": root_path},
            portal_type=self.portal_type,
        )

    def get_visualizations(self, obj):
        visualizations = getattr(obj, "visualizations", None)
        if isinstance(visualizations, str):
            try:
                visualizations = json.loads(visualizations)
            except ValueError:
                return visualizations
        return visualizations

    def has_visualizations(self, obj):
        visualizations = self.get_visualizations(obj)
        return bool(visualizations)

    def has_map_graphs(self, obj):
        return bool(getattr(obj, "map_graphs", None))

    def has_old_field_values(self, obj):
        return bool(
            getattr(obj, "map_graphs", None)
            or getattr(obj, "map_graphs_height", None)
            or getattr(obj, "map_graphs_full_width", False)
        )

    def migrate_visualization(self, obj):
        obj.visualizations = [
            {
                "title": "",
                "embed_code": getattr(obj, "map_graphs", "") or "",
                "height": getattr(obj, "map_graphs_height", "") or "",
                "full_width": bool(getattr(obj, "map_graphs_full_width", False)),
            }
        ]

    def clear_old_fields(self, obj):
        obj.map_graphs = None
        obj.map_graphs_height = None
        obj.map_graphs_full_width = False

    def update_obj(self, obj, migrate_visualization, clear_old_fields):
        if migrate_visualization:
            self.migrate_visualization(obj)
        if clear_old_fields:
            self.clear_old_fields(obj)
        modified(obj)
        obj.reindexObject()

    def result(self):
        if hasattr(self, "_result"):
            return self._result

        alsoProvides(self.request, IDisableCSRFProtection)

        change = self.should_change()
        language = self.get_language()
        path = self.get_path(language)
        root = self.get_root(language)

        if root is None:
            self._result = {
                "change": change,
                "language": language,
                "root_found": False,
                "path": path,
                "found": 0,
                "with_map_graphs": 0,
                "migrated": 0,
                "cleared_old_values": 0,
                "already_with_visualizations": 0,
                "without_map_graphs": 0,
            }
            logger.warning("Indicator visualizations root not found at %s", path)
            return self._result

        brains = self.get_brains(root)
        found = len(brains)
        with_map_graphs = 0
        migrated = 0
        cleared_old_values = 0
        already_with_visualizations = 0
        without_map_graphs = 0

        logger.info(
            "MigrateIndicatorVisualizations found %s indicators under %s. "
            "language=%s change=%s",
            found,
            root.absolute_url(),
            language,
            change,
        )

        for idx, brain in enumerate(brains, start=1):
            obj = brain.getObject()
            has_map_graphs = self.has_map_graphs(obj)
            has_visualizations = self.has_visualizations(obj)
            has_old_field_values = self.has_old_field_values(obj)

            if not has_map_graphs:
                without_map_graphs += 1
            else:
                with_map_graphs += 1

            if has_visualizations:
                already_with_visualizations += 1

            should_migrate_visualization = has_map_graphs and not has_visualizations
            should_clear_old_fields = has_old_field_values and (
                has_visualizations or should_migrate_visualization
            )

            if should_migrate_visualization:
                migrated += 1

            if should_clear_old_fields:
                cleared_old_values += 1

            if not should_migrate_visualization and not should_clear_old_fields:
                continue

            if change:
                self.update_obj(
                    obj,
                    should_migrate_visualization,
                    should_clear_old_fields,
                )

            if change and idx % 100 == 0:
                transaction.savepoint()

        if change:
            transaction.commit()

        self._result = {
            "change": change,
            "language": language,
            "root_found": True,
            "path": "/".join(root.getPhysicalPath()),
            "url": root.absolute_url(),
            "found": found,
            "with_map_graphs": with_map_graphs,
            "migrated": migrated,
            "cleared_old_values": cleared_old_values,
            "already_with_visualizations": already_with_visualizations,
            "without_map_graphs": without_map_graphs,
        }

        logger.info(
            "MigrateIndicatorVisualizations found=%s with_map_graphs=%s "
            "migrated=%s cleared_old_values=%s already_with_visualizations=%s "
            "without_map_graphs=%s language=%s change=%s",
            found,
            with_map_graphs,
            migrated,
            cleared_old_values,
            already_with_visualizations,
            without_map_graphs,
            language,
            change,
        )
        return self._result


class MigrateIndicatorVisualizationsLayout(BrowserView):
    """Add the visualizations metadata field to old Indicator Volto layouts."""

    path_template = "{language}"
    portal_type = "eea.climateadapt.indicator"
    legacy_field_ids = (
        "map_graphs",
        "map_graphs_height",
        "map_graphs_full_width",
    )
    visualization_field = {
        "@id": "d6d5ad7f-cd9d-4f36-b081-7619fdfeb0e7",
        "field": {
            "id": "visualizations",
            "title": "Visualizations",
            "widget": "json",
        },
    }

    def should_change(self):
        value = self.request.form.get("change", "")
        return value.lower() in ("1", "true", "yes", "on")

    def get_language(self):
        language = self.request.form.get("language", "en").strip().lower()
        if not re.match(r"^[a-z]{2}$", language):
            raise ValueError("language must be a two-letter code")
        return language

    def get_path(self, language):
        return self.path_template.format(language=language)

    def get_root(self, language):
        portal = api.portal.get()
        path = self.get_path(language)
        return portal.unrestrictedTraverse(path, None)

    def get_brains(self, root):
        if root is None:
            return []

        catalog = api.portal.get_tool("portal_catalog")
        root_path = "/".join(root.getPhysicalPath())
        return catalog.unrestrictedSearchResults(
            path={"query": root_path},
            portal_type=self.portal_type,
        )

    def field_id(self, field_entry):
        if not isinstance(field_entry, dict):
            return None
        field = field_entry.get("field")
        if not isinstance(field, dict):
            return None
        return field.get("id")

    def insert_visualization_field(self, fields):
        field_ids = [self.field_id(field) for field in fields]
        if "visualizations" in field_ids:
            return False

        insert_after = None
        for legacy_id in self.legacy_field_ids:
            if legacy_id in field_ids:
                insert_after = field_ids.index(legacy_id)

        if insert_after is None:
            return False

        fields.insert(insert_after + 1, deepcopy(self.visualization_field))
        return True

    def update_metadata_section(self, block):
        if not isinstance(block, dict):
            return False

        if block.get("@type") != "metadataSection":
            return False

        fields = block.get("fields")
        if not isinstance(fields, list):
            return False

        field_ids = [self.field_id(field) for field in fields]
        has_legacy_anchor = bool(set(field_ids).intersection(self.legacy_field_ids))
        if not has_legacy_anchor:
            return False

        return self.insert_visualization_field(fields)

    def update_blocks(self, obj, apply_changes):
        original_blocks = getattr(obj, "blocks", None)
        if not isinstance(original_blocks, dict):
            return {
                "changed": False,
                "added": 0,
            }

        blocks = deepcopy(original_blocks)
        stats = {
            "changed": False,
            "added": 0,
        }

        for block in visit_blocks(obj, blocks):
            if self.update_metadata_section(block):
                stats["added"] += 1

        stats["changed"] = blocks != original_blocks
        if stats["changed"] and apply_changes:
            obj.blocks = blocks
        return stats

    def result(self):
        if hasattr(self, "_result"):
            return self._result

        alsoProvides(self.request, IDisableCSRFProtection)

        change = self.should_change()
        language = self.get_language()
        path = self.get_path(language)
        root = self.get_root(language)

        if root is None:
            self._result = {
                "change": change,
                "language": language,
                "root_found": False,
                "path": path,
                "found": 0,
                "changed": 0,
                "visualization_fields_added": 0,
                "without_blocks": 0,
                "unchanged": 0,
                "sample_paths": [],
            }
            logger.warning("Indicator layout migration root not found at %s", path)
            return self._result

        brains = self.get_brains(root)
        found = len(brains)
        changed = 0
        visualization_fields_added = 0
        without_blocks = 0
        unchanged = 0
        sample_paths = []

        logger.info(
            "MigrateIndicatorVisualizationsLayout found %s indicators under %s. "
            "language=%s change=%s",
            found,
            root.absolute_url(),
            language,
            change,
        )

        for idx, brain in enumerate(brains, start=1):
            obj = brain.getObject()
            if not isinstance(getattr(obj, "blocks", None), dict):
                without_blocks += 1
                continue

            stats = self.update_blocks(obj, change)
            if not stats["changed"]:
                unchanged += 1
                continue

            changed += 1
            visualization_fields_added += stats["added"]

            if len(sample_paths) < 20:
                sample_paths.append("/".join(obj.getPhysicalPath()))

            if change:
                modified(obj)
                obj.reindexObject()

            if change and idx % 100 == 0:
                transaction.savepoint()

        if change:
            transaction.commit()

        self._result = {
            "change": change,
            "language": language,
            "root_found": True,
            "path": "/".join(root.getPhysicalPath()),
            "url": root.absolute_url(),
            "found": found,
            "changed": changed,
            "visualization_fields_added": visualization_fields_added,
            "without_blocks": without_blocks,
            "unchanged": unchanged,
            "sample_paths": sample_paths,
        }

        logger.info(
            "MigrateIndicatorVisualizationsLayout found=%s changed=%s "
            "added=%s without_blocks=%s unchanged=%s language=%s change=%s",
            found,
            changed,
            visualization_fields_added,
            without_blocks,
            unchanged,
            language,
            change,
        )
        return self._result


class CleanupIndicatorVisualizationsLayout(MigrateIndicatorVisualizationsLayout):
    """Remove old Indicator map/graphs fields from Volto layouts."""

    def remove_legacy_fields(self, fields):
        original_count = len(fields)
        fields[:] = [
            field
            for field in fields
            if self.field_id(field) not in self.legacy_field_ids
        ]
        return original_count - len(fields)

    def update_metadata_section(self, block):
        if not isinstance(block, dict):
            return 0

        if block.get("@type") != "metadataSection":
            return 0

        fields = block.get("fields")
        if not isinstance(fields, list):
            return 0

        return self.remove_legacy_fields(fields)

    def update_blocks(self, obj, apply_changes):
        original_blocks = getattr(obj, "blocks", None)
        if not isinstance(original_blocks, dict):
            return {
                "changed": False,
                "removed": 0,
            }

        blocks = deepcopy(original_blocks)
        stats = {
            "changed": False,
            "removed": 0,
        }

        for block in visit_blocks(obj, blocks):
            stats["removed"] += self.update_metadata_section(block)

        stats["changed"] = blocks != original_blocks
        if stats["changed"] and apply_changes:
            obj.blocks = blocks
        return stats

    def result(self):
        if hasattr(self, "_result"):
            return self._result

        alsoProvides(self.request, IDisableCSRFProtection)

        change = self.should_change()
        language = self.get_language()
        path = self.get_path(language)
        root = self.get_root(language)

        if root is None:
            self._result = {
                "change": change,
                "language": language,
                "root_found": False,
                "path": path,
                "found": 0,
                "changed": 0,
                "legacy_fields_removed": 0,
                "without_blocks": 0,
                "unchanged": 0,
                "sample_paths": [],
            }
            logger.warning("Indicator layout cleanup root not found at %s", path)
            return self._result

        brains = self.get_brains(root)
        found = len(brains)
        changed = 0
        legacy_fields_removed = 0
        without_blocks = 0
        unchanged = 0
        sample_paths = []

        logger.info(
            "CleanupIndicatorVisualizationsLayout found %s indicators under %s. "
            "language=%s change=%s",
            found,
            root.absolute_url(),
            language,
            change,
        )

        for idx, brain in enumerate(brains, start=1):
            obj = brain.getObject()
            if not isinstance(getattr(obj, "blocks", None), dict):
                without_blocks += 1
                continue

            stats = self.update_blocks(obj, change)
            if not stats["changed"]:
                unchanged += 1
                continue

            changed += 1
            legacy_fields_removed += stats["removed"]

            if len(sample_paths) < 20:
                sample_paths.append("/".join(obj.getPhysicalPath()))

            if change:
                modified(obj)
                obj.reindexObject()

            if change and idx % 100 == 0:
                transaction.savepoint()

        if change:
            transaction.commit()

        self._result = {
            "change": change,
            "language": language,
            "root_found": True,
            "path": "/".join(root.getPhysicalPath()),
            "url": root.absolute_url(),
            "found": found,
            "changed": changed,
            "legacy_fields_removed": legacy_fields_removed,
            "without_blocks": without_blocks,
            "unchanged": unchanged,
            "sample_paths": sample_paths,
        }

        logger.info(
            "CleanupIndicatorVisualizationsLayout found=%s changed=%s "
            "removed=%s without_blocks=%s unchanged=%s language=%s change=%s",
            found,
            changed,
            legacy_fields_removed,
            without_blocks,
            unchanged,
            language,
            change,
        )
        return self._result


class ImpactFiltersNew:
    """New impact filters"""

    # migrate_262157_impact_filter

    def list(self):
        response = []
        fileUploaded = self.request.form.get("fileToUpload", None)

        if not fileUploaded:
            return response

        data = fileUploaded.read().decode("utf-8")
        csv_file = io.StringIO(data)
        reader = csv.DictReader(csv_file)

        i_transaction = 0
        count_found = 0
        count_not_found = 0
        for row in reader:
            i_transaction += 1
            if i_transaction % 100 == 0:
                transaction.savepoint()

            # print(row)
            # import pdb
            # pdb.set_trace()

            item = {}
            item["uid"] = row["UID"]
            item["url"] = row["URL"]
            item["title"] = row["Title"]
            item["keywords"] = row["Keywords"]
            item["sectors"] = row["Sectors"]
            item["impacts"] = row["Impacts"]
            item["elements"] = row["Elements"]

            item["extreme_heat"] = row["EXTREME HEAT"]
            item["extreme_cold"] = row["EXTREME COLD"]
            item["wildfires"] = row["WILDFIRES"]
            item["non_specific"] = row["NON SPECIFIC"]

            obj = api.content.get(UID=item["uid"])

            if not obj:
                count_not_found += 1
                logger.info("NOT FOUND obj: %s", item["url"])
                continue
            count_found += 1

            # if '87d7dc67e16a4bc4b7320daf5ad670c9' == item['uid']:
            #     import pdb
            #     pdb.set_trace()

            changeMade = False
            if item["extreme_heat"] and "EXTREMEHEAT" not in obj.climate_impacts:
                obj.climate_impacts.append("EXTREMEHEAT")
                changeMade = True
            if item["extreme_cold"] and "EXTREMECOLD" not in obj.climate_impacts:
                obj.climate_impacts.append("EXTREMECOLD")
                changeMade = True
            if item["wildfires"] and "WILDFIRES" not in obj.climate_impacts:
                obj.climate_impacts.append("WILDFIRES")
                changeMade = True
            if item["non_specific"] and "NONSPECIFIC" not in obj.climate_impacts:
                obj.climate_impacts.append("NONSPECIFIC")
                changeMade = True

            if obj.climate_impacts and "EXTREMETEMP" in obj.climate_impacts:
                obj.climate_impacts.remove("EXTREMETEMP")
                changeMade = True

            if changeMade:
                obj._p_changed = True

            response.append(
                {
                    "title": obj.title,
                    "url": item["url"],
                    "funding_programme": obj.title,
                }
            )
            logger.info("OBJ: %s", obj.absolute_url())

        transaction.commit()

        logger.info(
            "LINES IN RESPONSE: %s, FOUND %s, NOTFOUND %s",
            len(response),
            count_found,
            count_not_found,
        )
        return response


class ToolExtendFields:
    """New fields for tool #304613"""

    _headers = []

    def get_value_by_header(self, line, key):
        index = None
        try:
            index = self._headers.index(key)
        except ValueError:
            return None

        return line[index] if 0 <= index < len(line) else None

    def get_obj_sectors(self, row):
        map_header = [
            ("AGRICULTURE", "16. Sector_Agriculture"),
            ("BIODIVERSITY", "16. Sector_Biodiversity"),
            ("BUILDINGS", "16. Sector_Buildings"),
            ("BUSINESSINDUSTRY", "16. Sector_Business & Industry"),
            ("COASTAL", "16. Sector_Coastal areas"),
            ("CULTURALHERITAGE", "16. Sector_Cultural heritage"),
            ("DISASTERRISKREDUCTION", "16. Sector_Disaster Risk Reduction"),
            ("ECOSYSTEMSRESTORATION", ""),
            ("ENERGY", "16. Sector_Energy"),
            ("FINANCIAL", "16. Sector_Financial"),
            ("FORESTRY", "16. Sector_Forestry"),
            ("HEALTH", "16. Sector_Health"),
            ("ICT", "16. Sector_ICT"),
            ("LANDUSE", "16. Sector_Land use planning"),
            ("MARINE", "16. Sector_Marine & fisheries"),
            ("MOUNTAINAREAS", "16. Sector_Mountain areas"),
            ("TOURISMSECTOR", "16. Sector_Tourism"),
            ("TRANSPORT", "16. Sector_Transport"),
            ("URBAN", "16. Sector_Urban"),
            ("WATERMANAGEMENT", "16. Sector_Water management"),
            ("NONSPECIFIC", ""),
        ]

        response = []
        for key, header_name in map_header:
            if header_name == "":
                continue
            val = self.get_value_by_header(row, header_name)
            if val and val.strip().upper() == "Y":
                response.append(key)
        return response

    def get_obj_climateimpacts(self, row):
        map_header = [
            ("DROUGHT", "11. Hazard_Drought"),
            ("EXTREMEHEAT", "11. Hazard_Heat"),
            ("EXTREMECOLD", "11. Hazard_Cold waves / extreme cold"),
            ("FLOODING", "11. Hazard_Flooding"),
            ("ICEANDSNOW", "11. Hazard_Snow/Avalanche"),
            ("SEALEVELRISE", "11. Hazard_Sea-level rise"),
            ("STORM", "11. Hazard_Coastal flooding / storm surge"),
            ("WATERSCARCE", ""),
            ("WILDFIRES", "11. Hazard_Fire / wildfire"),
            ("NONSPECIFIC", "11. Hazard_Not hazard-specific"),
        ]

        response = []
        for key, header_name in map_header:
            if header_name == "":
                continue
            val = self.get_value_by_header(row, header_name)
            if val and val.strip().upper() == "Y":
                response.append(key)
        return response

    def get_obj_intended_user_groups(self, row):
        map_header = [
            (
                "COMMISSION_SERVICE_AND_OR_AGENCIES",
                "6. Intended User Groups_Commission services and/or Agencies",
            ),
            (
                "TRANSBOUNDARY_NETWORK",
                "6. Intended User Groups_ Transboundary networks",
            ),
            ("NATIONAL_AUTHORITIES", "6. Intended User Groups_National authorities"),
            (
                "SUBNATIONAL_AUTHORITIES",
                "6. Intended User Groups_Subnational authorities  [Y/N]",
            ),
            (
                "BUSINESSES_CONSULTANTS",
                "6. Intended User Groups_Businesses/consultants  [Y/N]",
            ),
            (
                "RESEASRCHERS_SUPPORTING_POLICY",
                "6. Intended User Groups_Researchers supporting policy  [Y/N]",
            ),
            ("NGOS", "6. Intended User Groups_NGOs [Y/N]"),
            ("CITIZENS", "6. Intended User Groups_Citizens [Y/N]"),
        ]

        response = []
        for key, header_name in map_header:
            if header_name == "":
                continue
            val = self.get_value_by_header(row, header_name)
            if val and val.strip().upper() == "Y":
                response.append(key)
        return response

    def get_obj_place_of_implementation(self, row):
        map_header = [
            ("GLOBAL_LEVEL", "7. Place of implementation_Global level"),
            (
                "EUROPEAN_LEVEL",
                "7. Place of implementation_European level",
            ),
            (
                "TRANSNATIONAL",
                "7. Place of implementation_transnational ((convention-based) shared coastal, mountain, sea regions -e-g- mediterrenean etc",
            ),
            (
                "OUTERMOST_EUROPEAN_REGIONS",
                "7. Place of implementation_Outermost European regions",
            ),
            ("NATIONAL_LEVEL", "7. Place of implementation_national-level"),
            ("SUBNATIONAL", "7. Place of implementation_subnational"),
        ]

        response = []
        for key, header_name in map_header:
            if header_name == "":
                continue
            val = self.get_value_by_header(row, header_name)
            if val and val.strip().upper() == "Y":
                response.append(key)
        return response

    def get_obj_adaptation_support_cycle_step(self, row):
        map_header = [
            (
                "STEP_1",
                "17. Adaptation Support Cycle Step_Step 1: Preparing the Ground for Adaptation",
            ),
            (
                "STEP_2",
                "17. Adaptation Support Cycle Step_Step 2: Assessing Climate Change Risks and Vulnerabilities",
            ),
            (
                "STEP_3",
                "17. Adaptation Support Cycle Step_Step 3: Identifying Adaptation Options",
            ),
            (
                "STEP_4",
                "17. Adaptation Support Cycle Step_Step 4: Assessing and Prioritising Adaptation Options",
            ),
            ("STEP_5", "17. Adaptation Support Cycle Step_Step 5: Implementation"),
            (
                "STEP_6",
                "17. Adaptation Support Cycle Step_Step 6: Monitoring and Evaluation (M&E)",
            ),
        ]

        response = []
        for key, header_name in map_header:
            if header_name == "":
                continue
            val = self.get_value_by_header(row, header_name)
            if val and val.strip().upper() == "Y":
                response.append(key)
        return response

    def get_obj_type_of_data(self, row):
        map_header = [
            ("OBSERVATIONAL_DATASETS", "8. Type of data_Observational datasets"),
            ("REANALYSIS_DATASETS", "8. Type of data_Reanalysis datasets"),
            (
                "CLIMATE_MODEL_OUTPUTS",
                "8. Type of data_Climate model outputs (simulations of past or present climate, scenarios, projections)",
            ),
            (
                "IMPACT_OR_SECTORAL_MODEL_OUTPUTS",
                "8. Type of data_Impact or sectoral model outputs (e.g. flood, crop, wildfire models)",
            ),
            (
                "SOCIO_ECONOMIC",
                "8. Type of data_Socio-economic or exposure data (e.g. population, assets, land use)",
            ),
            ("OTHER", "8. Type of data_Other"),
        ]

        response = []
        for key, header_name in map_header:
            if header_name == "":
                continue
            val = self.get_value_by_header(row, header_name)
            if val and val.strip().upper() == "Y":
                response.append(key)
        return response

    def get_obj_data_sources(self, row):
        map_header = [
            (
                "PUBLIC_DATASETS",
                "9. Data sources_Public datasets from external providers (e.g. Copernicus, national meteorological services)",
            ),
            (
                "PROJECT_GENERATED",
                "9. Data sources_Project-generated or processed datasets (data created or processed by the tool developers)",
            ),
            (
                "USER_PROVIDED",
                "9. Data sources_User-provided input data (e.g. uploaded assets, local datasets, reported data)",
            ),
            (
                "COMERCIAL_OR_THIRD_PARTY",
                "9. Data sources_Commercial or third-party data providers",
            ),
            ("MIXED_SOURCES", "9. Data sources_Mixed sources"),
        ]

        response = []
        for key, header_name in map_header:
            if header_name == "":
                continue
            val = self.get_value_by_header(row, header_name)
            if val and val.strip().upper() == "Y":
                response.append(key)
        return response

    def get_obj_license_status(self, row):
        map_header = [
            (
                "FULLY_OPEN",
                "10. License status_Fully open data (freely available without restrictions)",
            ),
            ("OPEN_DATA", "10. License status_Open data with attribution requirements"),
            (
                "LICENSED_OR_COMMERCIAL",
                "10. License status_Licensed or commercial data",
            ),
            ("RESTRICTED", "10. License status_Restricted"),
            (
                "MIXED",
                "10. License status_Mixed (combination of open and restricted data)",
            ),
        ]

        response = []
        for key, header_name in map_header:
            if header_name == "":
                continue
            val = self.get_value_by_header(row, header_name)
            if val and val.strip().upper() == "Y":
                response.append(key)
        return response

    def get_obj_type_of_outputs(self, row):
        map_header = [
            ("MAPS_AND_GRAPHS", "19. Type of outputs_Maps and graphs"),
            (
                "REPORTS_AND_DECISION_SUPPORT",
                "19. Type of outputs_Reports and decision support",
            ),
            ("DATASETS_AND_INDICATORS", "19. Type of outputs_Datasets and indicators"),
            ("NARRATIVES", "19. Type of outputs_Narratives"),
            ("BEST_PRACTICE_EXAMPLES", "19. Type of outputs_Best practice examples"),
        ]

        response = []
        for key, header_name in map_header:
            if header_name == "":
                continue
            val = self.get_value_by_header(row, header_name)
            if val and val.strip().upper() == "Y":
                response.append(key)
        return response

    def get_obj_temporality_of_data(self, row):
        map_header = [
            ("HISTORYCAL_PAST", "20. Temporality of data_Historical/past"),
            ("PRESENT", "20. Temporality of data_Present"),
            ("FORWARD_LOOKING", "20. Temporality of data_Forward-looking"),
        ]

        response = []
        for key, header_name in map_header:
            if header_name == "":
                continue
            val = self.get_value_by_header(row, header_name)
            if val and val.strip().upper() == "Y":
                response.append(key)
        return response

    def get_obj_user_support_provisions(self, row):
        map_header = [
            (
                "USER_GUIDANCE",
                "12. User support provisions_User guidance / documentation",
            ),
            ("HELPDESK", "12. User support provisions_Helpdesk / contact support"),
            ("TUTORIALS", "12. User support provisions_Tutorials / training material"),
            (
                "INTERACTIVE_ASSISTANCE",
                "12. User support provisions_Interactive assistance (chatbot / wizard)",
            ),
        ]

        response = []
        for key, header_name in map_header:
            if header_name == "":
                continue
            val = self.get_value_by_header(row, header_name)
            if val and val.strip().upper() == "Y":
                response.append(key)
        return response

    def get_obj_tool_validation_use(self, row):
        map_header = [
            (
                "PEER_REVIEWED_METHODOLOGY",
                "13. Tool validation use_Peer-reviewed methodology",
            ),
            ("CASE_STUDY_VALIDATION", "13. Tool validation use_Case-study validation"),
            (
                "EXPERT_VALIDATION",
                "13. Tool validation use_Expert validation / reputable institution",
            ),
            ("USER_TESTING", "13. Tool validation use_User testing / pilot testing"),
        ]

        response = []
        for key, header_name in map_header:
            if header_name == "":
                continue
            val = self.get_value_by_header(row, header_name)
            if val and val.strip().upper() == "Y":
                response.append(key)
        return response

    def get_obj_number_of_users_tool(self, row):
        map_header = [
            ("HIGH_UPTAKE", "14. Number of users / uptake (if known)_High uptake"),
            ("MEDIUM_UPTAKE", "14. Number of users / uptake (if known)_Medium uptake"),
            ("LOW_UPTAKE", "14. Number of users / uptake (if known)_Low uptake"),
            ("UNKNOWN", "14. Number of users / uptake (if known)_Unknown"),
        ]

        response = []
        for key, header_name in map_header:
            if header_name == "":
                continue
            val = self.get_value_by_header(row, header_name)
            if val and val.strip().upper() == "Y":
                response.append(key)
        return response

    def get_obj_tool_provider_mode(self, row):
        map_header = [
            (
                "PUBLIC",
                "15. Tool provider [private, public, both, other]_Public organisation",
            ),
            (
                "PRIVATE",
                "15. Tool provider [private, public, both, other]_Private organisation",
            ),
            (
                "PUBLIC_PRIVATE",
                "15. Tool provider [private, public, both, other]_Public-private partnership",
            ),
            ("OTHER", "15. Tool provider [private, public, both, other]_Other"),
        ]

        response = []
        for key, header_name in map_header:
            if header_name == "":
                continue
            val = self.get_value_by_header(row, header_name)
            if val and val.strip().upper() == "Y":
                response.append(key)
        return response

    def get_obj_tool_accessibility_and_usability(self, row):
        map_header = [
            (
                "HIGH",
                "26. Accessibility and usability_High (general user-friendly, minimal technical knowledge needed)",
            ),
            (
                "MODERATE",
                "26. Accessibility and usability_Moderate (some prior technical/scientific knowledge needed)",
            ),
            (
                "LOW",
                "26. Accessibility and usability_Low (high-level expertise needed)",
            ),
        ]

        response = None
        for key, header_name in map_header:
            if header_name == "":
                continue
            val = self.get_value_by_header(row, header_name)
            if val and val.strip().upper() == "Y":
                response = key
        return response

    def process_region(self, val):
        val = val.strip()
        val_lower = val.lower()

        # 1. Global / Europe
        is_global = ""
        if "global" in val_lower or "international" in val_lower:
            is_global = "Global"
        elif "europe" in val_lower or "european" in val_lower:
            is_global = "Europe"

        # 2. Country
        country_names = []
        country_codes = []

        # Check for country codes
        matches = re.findall(r"\b([A-Z]{2})\b", val)
        for code in matches:
            orig_code = code
            if code == "UK":
                code = "GB"
            elif code == "EL":
                code = "GR"
            c = pycountry.countries.get(alpha_2=code)
            if c and c.name not in country_names:
                country_names.append(c.name)
                country_codes.append(c.alpha_2)

        # Check if country name is in the string
        for c in pycountry.countries:
            if c.name.lower() in val_lower and c.name not in country_names:
                country_names.append(c.name)
                country_codes.append(c.alpha_2)

        for code in country_codes:
            if code in european_countries:
                is_global = "Europe"
                break

        # 3. Subnational Key
        subnational_key = ""
        best_key = ""
        best_score = 0

        # Simple normalization to find overlapping meaningful words
        def normalize(text):
            text = re.sub(r"[^a-zA-Z0-9\s]", " ", text).lower()
            # ignore generic words like region, area, selected, cities
            ignore_words = {
                "region",
                "area",
                "selected",
                "cities",
                "city",
                "level",
                "national",
            }
            words = set(
                [w for w in text.split() if len(w) > 3 and w not in ignore_words]
            )
            return words

        val_words = normalize(val)

        if val_words:
            for key, name in SUBNATIONAL_REGIONS.items():
                name_words = normalize(name)
                intersection = val_words.intersection(name_words)
                if len(intersection) > best_score:
                    best_score = len(intersection)
                    best_key = key

        if best_score > 0:
            subnational_key = best_key

        return is_global, country_names, country_codes, subnational_key

    def list(self):
        response = []
        fileUploaded = self.request.form.get("fileToUpload", None)

        if not fileUploaded:
            return response

        data = fileUploaded.read().decode("utf-8")
        csv_file = io.StringIO(data)

        reader = csv.reader(csv_file)

        # first two rows are headers
        header1 = next(reader)
        header2 = next(reader)

        last_header = ""

        for a, b in zip(header1, header2):
            b.replace("\xa0", " ").strip() if b else b
            if a:
                last_header = a.strip()
            value = f"{last_header}_{b}" if b else last_header
            value = value.replace("\xa0", "").strip()
            self._headers.append(value)

        import pdb

        # pdb.set_trace()

        i_transaction = 0
        for row in reader:
            i_transaction += 1

            if i_transaction % 100 == 0:
                transaction.savepoint()

            if self.get_value_by_header(row, "Tool ID") == "":
                continue

            item = {}
            item["external_id"] = self.get_value_by_header(row, "Tool ID")
            item["name"] = self.get_value_by_header(row, "Name of tool")
            item["short_description"] = self.get_value_by_header(
                row, "Short description"
            )

            # pdb.set_trace()
            item["sectors"] = self.get_obj_sectors(row)

            if not item["sectors"]:
                print("No sectors for:" + item["external_id"])
                continue

            catalog = self.context.portal_catalog
            brains = catalog.unrestrictedSearchResults(
                path="/cca/en",
                portal_type=["eea.climateadapt.tool", "eea.climateadapt.extendedtool"],
            )
            obj = None

            for brain in brains:
                _obj = brain.getObject()
                if getattr(_obj, "external_id", None) == item["external_id"]:
                    obj = brain.getObject()

            # if item["external_id"] == "#14":
            #     pdb.set_trace()

            if not obj:
                container = api.content.get(path="/cca/en/metadata/tools/")

                obj = api.content.create(
                    container=container,
                    type="eea.climateadapt.extendedtool",
                    portal_type="eea.climateadapt.extendedtool",
                    sectors=item["sectors"],
                    climate_impacts=["EXTREMEHEAT"],
                    publication_date=date(2026, 1, 1),
                    title=item["name"],
                    external_id=item["external_id"],
                    safe_id=True,
                )
                obj.external_id = item["external_id"]

                logger.info("CREATED: %s -> %s", item["external_id"], item["name"])

            obj.climate_impacts = self.get_obj_climateimpacts(row)
            obj.spatial_resolution = self.get_value_by_header(
                row, "21. Spatial resolution_Free text (Local, NUTS3, NUTS2…)"
            )
            obj.underlying_data_maintenance = self.get_value_by_header(
                row, "22. Underlying data maintenance_Free text"
            )
            if self.get_value_by_header(row, "23. Nature-based solution_Check (Y/N)"):
                obj.nature_based_solution = (
                    self.get_value_by_header(
                        row, "23. Nature-based solution_Check (Y/N)"
                    ).upper()
                    == "Y"
                )
            obj.just_resilience = (
                self.get_value_by_header(row, "24. Just resilience_Check (Y/N)").upper()
                == "Y"
            )
            obj.cost_benefit_ratio = (
                self.get_value_by_header(
                    row, "25. Cost-benefit ratio_Check (Y/N)"
                ).upper()
                == "Y"
            )
            # if item["external_id"] == "#14":
            #     pdb.set_trace()
            functionality_value = self.get_value_by_header(
                row, "27. Functionality_Number of adaptation support cycle steps"
            )
            obj.functionality = (
                None
                if functionality_value and functionality_value == ""
                else int(functionality_value)
            )
            obj.strengths_and_possible_limitations = self.get_value_by_header(
                row, "28. Strengths and possible limitations of the tool_Free text"
            )

            # pdb.set_trace()
            obj.tool_provider = self.get_value_by_header(row, "Tool provider")
            obj.public_private_mode = self.get_value_by_header(row, "public/private")
            obj.contact = self.get_value_by_header(row, "Contact (person / email)")
            obj.hyperlink = self.get_value_by_header(row, "Tool hyperlink")
            obj.coder_1 = self.get_value_by_header(row, "CODER 1")
            obj.coder_2 = self.get_value_by_header(row, "CODER 1_CODER 2")

            obj.intended_user_groups = self.get_obj_intended_user_groups(row)
            obj.place_of_implementation = self.get_obj_place_of_implementation(row)
            obj.type_of_data = self.get_obj_type_of_data(row)
            obj.data_sources = self.get_obj_data_sources(row)
            obj.license_status = self.get_obj_license_status(row)
            obj.adaptation_support_cycle_step = (
                self.get_obj_adaptation_support_cycle_step(row)
            )

            # obj.description = item["short_description"]
            # TODO: this is mandatory for update !?
            obj.long_description = RichTextValue(
                raw="<p>" + item["short_description"] + "</p>",
                mimeType="text/html",
                outputMimeType="text/html",
            )

            obj.sectors = item["sectors"]
            obj.tool_available_english = (
                self.get_value_by_header(
                    row, "18. In which language(s) is the tool available?_English"
                )
                and self.get_value_by_header(
                    row, "18. In which language(s) is the tool available?_English"
                ).upper()
                == "Y"
            )

            obj.tool_available_language = self.get_value_by_header(
                row,
                "18. In which language(s) is the tool available?_Other EU/EEA member/cooperating country language",
            )
            obj.type_of_outputs = self.get_obj_type_of_outputs(row)
            obj.temporality_of_data = self.get_obj_temporality_of_data(row)
            obj.user_support_provisions = self.get_obj_user_support_provisions(row)
            obj.tool_validation_use = self.get_obj_tool_validation_use(row)
            obj.number_of_users_tool = self.get_obj_number_of_users_tool(row)
            obj.tool_provider_mode = self.get_obj_tool_provider_mode(row)

            obj.only_interactive_support_tool = (
                self.get_value_by_header(
                    row, "1. Only *online* interactive support tool"
                ).upper()
                == "Y"
            )
            obj.adaptation_cycle_step = (
                self.get_value_by_header(
                    row, "2. Supports ≥1 adaptation cycle step"
                ).upper()
                == "Y"
            )
            obj.updating_cycle_of_the_tool = (
                self.get_value_by_header(
                    row, "3. Updating cycle of the tool (Tools <5 years and up to date)"
                ).upper()
                == "Y"
            )
            obj.language_accessibility = (
                self.get_value_by_header(row, "4. Language Accessibility (EEA)").upper()
                == "Y"
            )
            obj.free_access = (
                self.get_value_by_header(
                    row, "5. Free [full or core functionality] access"
                ).upper()
                == "Y"
            )
            obj.accessibility_and_usability = (
                self.get_obj_tool_accessibility_and_usability(row)
            )

            # pdb.set_trace()
            is_global, country_names, country_codes, subnational_key = (
                self.process_region(
                    self.get_value_by_header(row, "Geographic coverage/scope")
                )
            )

            geochars = json.loads(obj.geochars)
            geochars["geoElements"]["element"] = is_global.upper()
            if country_codes:
                geochars["geoElements"]["countries"] = country_codes
            if subnational_key:
                geochars["geoElements"]["subnational"] = [subnational_key]
            else:
                geochars["geoElements"]["subnational"] = []
            geochars = json.dumps(geochars).encode()
            obj.geochars = geochars

            obj._p_changed = True
            obj.reindexObject()

            logger.info("OBJ URL: %s", obj.absolute_url())
            response.append(
                {
                    "external_id": item["external_id"],
                    "name": item["name"],
                    "url": obj.absolute_url(),
                }
            )
            logger.info("OBJ: %s -> %s", item["external_id"], item["name"])

        transaction.commit()

        logger.info(
            "LINES IN RESPONSE: %s",
            len(response),
        )
        return response


class FixMipSigLangs(BrowserView):
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        catalog = self.context.portal_catalog
        brains = catalog.unrestrictedSearchResults(
            path="/cca/en", portal_type="mission_signatory_profile"
        )
        for brain in brains:
            obj = brain.getObject()
            ILanguage(obj).set_language("en")
            catalog.reindexObject(obj, idxs=["Language"])
            logger.info(f"Fixed %s", brain.getURL())

        if not self.request.form.get("write"):
            raise ValueError

        return "done"


class MigrateAdaptationOption(BrowserView):
    """Migrate show_related_resources field (refs #296805)"""

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        catalog = api.portal.get_tool("portal_catalog")

        brains = catalog.unrestrictedSearchResults(
            portal_type="eea.climateadapt.adaptationoption"
        )

        count = 0
        total = len(brains)
        logger.info("Found %s AdaptationOption items", total)

        for idx, brain in enumerate(brains, start=1):
            obj = brain.getObject()

            if getattr(obj, "show_related_resources", None) is not False:
                obj.show_related_resources = False
                obj._p_changed = True
                count += 1
                logger.info("Updated %s", brain.getURL())

            if idx % 100 == 0:
                transaction.savepoint()

        transaction.commit()

        msg = f"Updated {count} out of {total} AdaptationOption items show_related_resources field"
        logger.info(msg)
        return msg


class MigrateMoldovaUkraineGeoCoverage(BrowserView):
    """Migrate Moldova and Ukraine geographical coverage."""

    macro_region = "TRANS_MACRO_DANUBE"
    countries = ("MD", "UA")

    def should_change(self):
        value = self.request.form.get("change", "")
        return value.lower() in ("1", "true", "yes", "on")

    def get_brains(self):
        catalog = api.portal.get_tool("portal_catalog")
        return catalog.unrestrictedSearchResults(macro_regions=self.macro_region)

    def update_geochars(self, obj):
        raw_geochars = getattr(obj, "geochars", None)
        if not raw_geochars:
            return None, "Missing geochars"

        try:
            geochars = json.loads(raw_geochars)
        except Exception as error:
            return None, "Invalid geochars: {}".format(error)

        geo_elements = geochars.get("geoElements", {})
        macrotrans = geo_elements.get("macrotrans") or []

        if self.macro_region not in macrotrans:
            return None, "Danube Region not found in geochars"

        current_countries = geo_elements.get("countries") or []
        missing_countries = [
            country for country in self.countries if country not in current_countries
        ]

        if not missing_countries:
            return None, "Already has Moldova and Ukraine"

        geo_elements["countries"] = current_countries + missing_countries
        geochars["geoElements"] = geo_elements

        return json.dumps(geochars), ""

    def list(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        change = self.should_change()
        response = []
        changed = 0

        brains = self.get_brains()
        total = len(brains)

        logger.info(
            "MigrateMoldovaUkraineGeoCoverage found %s Danube Region items. change=%s",
            total,
            change,
        )

        for idx, brain in enumerate(brains, start=1):
            obj = brain.getObject()
            updated_geochars, error = self.update_geochars(obj)

            if not updated_geochars:
                if error and "Danube Region not found" not in error:
                    logger.info("Skipped %s: %s", brain.getURL(), error)
                continue

            old_geochars = getattr(obj, "geochars", "")

            if change:
                obj.geochars = updated_geochars
                obj._p_changed = True
                obj.reindexObject()
                changed += 1

                if idx % 100 == 0:
                    transaction.savepoint()

            response.append(
                {
                    "nr": len(response) + 1,
                    "title": obj.title,
                    "url": brain.getURL(),
                    "portal_type": brain.portal_type,
                    "old_geochars": old_geochars,
                    "new_geochars": updated_geochars,
                    "changed": "Y" if change else "N",
                }
            )

        if change:
            transaction.commit()

        logger.info(
            "MigrateMoldovaUkraineGeoCoverage %s %s out of %s Danube Region items",
            "changed" if change else "would change",
            changed if change else len(response),
            total,
        )

        return response
