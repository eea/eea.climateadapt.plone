"""Import extended tools from ODS spreadsheets into Climate-ADAPT.

Combines data from two source spreadsheets:
1. Main metadata spreadsheet (sectors, hazards, user groups, geographic scope, etc.)
2. Extra fields spreadsheet ("What you can do with it", "Why it's relevant", "Already applied to")

Can be run as a CLI script or imported by browser migration views.
"""

import argparse
import html
import io
import json
import logging
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from datetime import date

import pycountry
import transaction
from plone import api
from plone.app.textfield.value import RichTextValue

from eea.climateadapt.vocabulary import (
    SUBNATIONAL_REGIONS,
    european_countries,
)

logger = logging.getLogger("eea.climateadapt.importer.extended_tools")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def split_bullets(text_list):
    """Split text into individual bullet items."""
    bullets = []
    for text in text_list:
        if not text:
            continue
        if "•" in text:
            parts = re.split(r"•\s*", text)
            for p in parts:
                p = p.strip()
                if p:
                    bullets.append(p)
        else:
            for line in text.split("\n"):
                line = line.strip().lstrip("-*•").strip()
                if line:
                    bullets.append(line)
    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for b in bullets:
        if b not in seen:
            seen.add(b)
            deduped.append(b)
    return deduped


def to_richtext_list(bullets):
    """Convert bullet points list to RichTextValue containing <ul><li>...</li></ul>."""
    if not bullets:
        return None
    items = "".join(f"<li>{html.escape(b)}</li>" for b in bullets)
    html_raw = f"<ul>{items}</ul>"
    return RichTextValue(
        raw=html_raw,
        mimeType="text/html",
        outputMimeType="text/html",
    )


def to_richtext_text(text):
    """Convert text paragraph to RichTextValue containing <p>...</p>."""
    if not text or not text.strip():
        return None
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [text.strip()]
    html_raw = "".join(f"<p>{html.escape(p)}</p>" for p in paragraphs)
    return RichTextValue(
        raw=html_raw,
        mimeType="text/html",
        outputMimeType="text/html",
    )


def parse_ods_rows(file_or_path):
    """Parse rows from an ODS file, including covered-table-cells from merged rows."""
    if isinstance(file_or_path, (str, os.PathLike)):
        z = zipfile.ZipFile(file_or_path, "r")
    elif isinstance(file_or_path, bytes):
        z = zipfile.ZipFile(io.BytesIO(file_or_path), "r")
    elif hasattr(file_or_path, "read"):
        data = file_or_path.read()
        z = zipfile.ZipFile(io.BytesIO(data), "r")
    else:
        raise TypeError(f"Unsupported type for file_or_path: {type(file_or_path)}")

    with z:
        tree = ET.fromstring(z.read("content.xml"))
        namespaces = {
            "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
        }
        for t in tree.findall(".//table:table", namespaces):
            rows = t.findall(".//table:table-row", namespaces)
            all_rows = []
            for r in rows:
                cells = []
                for child in r:
                    tag = child.tag.split("}")[-1]
                    if tag in ("table-cell", "covered-table-cell"):
                        rep = int(
                            child.attrib.get(
                                "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}number-columns-repeated",
                                1,
                            )
                        )
                        txt = "\n".join(child.itertext()).strip()
                        cells.extend([txt] * min(rep, 100))
                all_rows.append(cells)
            return all_rows
    return []


class ExtendedToolsImporter:
    """Parser and importer for extended tools."""

    def __init__(self):
        self._headers = []

    def get_value_by_header(self, line, key):
        """Lookup column value by header name."""
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
            if not header_name:
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
            if not header_name:
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
                "6. Intended User Groups_Transboundary networks",
            ),
            ("NATIONAL_AUTHORITIES", "6. Intended User Groups_National authorities"),
            (
                "SUBNATIONAL_AUTHORITIES",
                "6. Intended User Groups_Subnational authorities [Y/N]",
            ),
            (
                "BUSINESSES_CONSULTANTS",
                "6. Intended User Groups_Businesses/consultants [Y/N]",
            ),
            (
                "RESEASRCHERS_SUPPORTING_POLICY",
                "6. Intended User Groups_Researchers supporting policy [Y/N]",
            ),
            ("NGOS", "6. Intended User Groups_NGOs [Y/N]"),
            ("CITIZENS", "6. Intended User Groups_Citizens [Y/N]"),
        ]
        response = []
        for key, header_name in map_header:
            if not header_name:
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
                "7. Place of implementation_transnational ((convention-based) shared coastal, mountain, sea regions -e-g- mediterrenean etc)",
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
            if not header_name:
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
                "8. Type of data_Climate model outputs (simulations of past or present climate; scenarios; projections)",
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
            if not header_name:
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
            if not header_name:
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
            (
                "OPEN_DATA",
                "10. License status_Open data with attribution requirements",
            ),
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
            if not header_name:
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
            if not header_name:
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
            if not header_name:
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
            if not header_name:
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
            if not header_name:
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
            if not header_name:
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
            if not header_name:
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
            if not header_name:
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
            if not header_name:
                continue
            val = self.get_value_by_header(row, header_name)
            if val and val.strip().upper() == "Y":
                response = key
        return response

    def process_region(self, val):
        if not val:
            return "", [], [], "", [], ""
        val = val.strip()
        val_lower = " ".join(val.lower().split())

        # 1. Macro-Transnational / Transnational regions
        macro_map = {
            "transnational (alpine)": "TRANS_MACRO_ALP_SPACE",
            "alpine region": "TRANS_MACRO_ALP_SPACE",
            "central europe": "TRANS_MACRO_CEN_EUR",
            "outermost european regions": "TRANS_MACRO_OUTERMOST",
        }
        macro_regions = []
        for k, v in macro_map.items():
            if k in val_lower and v not in macro_regions:
                macro_regions.append(v)

        # 2. Global / Europe
        is_global = (
            "Global"
            if ("global" in val_lower or "international" in val_lower)
            else "Europe"
        )

        # 3. Country
        country_names = []
        country_codes = []

        matches = re.findall(r"\b([A-Z]{2})\b", val)
        for code in matches:
            if code == "UK":
                code = "GB"
            elif code == "EL":
                code = "GR"
            c = pycountry.countries.get(alpha_2=code)
            if c and c.name not in country_names:
                country_names.append(c.name)
                country_codes.append(c.alpha_2)

        for c in pycountry.countries:
            if c.name.lower() in val_lower and c.name not in country_names:
                country_names.append(c.name)
                country_codes.append(c.alpha_2)

        for code in country_codes:
            if code in european_countries:
                is_global = "Europe"
                break

        # 4. Subnational Key
        subnational_key = ""
        best_key = ""
        best_score = 0

        def normalize(text):
            text = re.sub(r"[^a-zA-Z0-9\s]", " ", text).lower()
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

        # 5. Residual free text treated as municipality name (city)
        residual = val
        residual = re.sub(
            r"(?i)\b(?:country|selected\s+region|region):\s*", " ", residual
        )
        residual = re.sub(r"(?i)\b(?:country)/\s*", " ", residual)
        for k in macro_map:
            residual = re.sub(rf"(?i){re.escape(k)}", " ", residual)
        for code in matches:
            residual = re.sub(rf"\b{code}\b", " ", residual)
        for name in country_names:
            residual = re.sub(rf"(?i)\b{re.escape(name)}\b", " ", residual)
        if subnational_key:
            sub_name = SUBNATIONAL_REGIONS[subnational_key]
            residual = re.sub(rf"(?i){re.escape(sub_name)}", " ", residual)
            for w in normalize(sub_name):
                residual = re.sub(rf"(?i)\b{re.escape(w)}\b", " ", residual)
        residual = re.sub(
            r"(?i)\b(?:global|international|europe|european)\b", " ", residual
        )
        residual = re.sub(r"[;,+/\(\)]", " ", residual)
        residual = " ".join(residual.split()).strip()
        if residual.lower() in {"city", "cities", "municipality", "area", "region"}:
            residual = ""

        city = residual.capitalize() if residual else ""

        return (
            is_global,
            country_names,
            country_codes,
            subnational_key,
            macro_regions,
            city,
        )

    def parse_file1_rows(self, rows):
        """Parse main metadata rows from File 1 (ODS rows or CSV reader)."""
        if len(rows) < 3:
            return {}

        header1 = rows[0]
        header2 = rows[1]
        self._headers = []
        last_header = ""
        for a, b in zip(header1, header2):
            if a:
                last_header = a.strip()
            value = f"{last_header}_{b}" if b else last_header
            value = value.replace("\xa0", "").strip()
            self._headers.append(value)

        tools = {}
        for row in rows[2:]:
            if not row or not any(row):
                continue
            raw_id = self.get_value_by_header(row, "Tool ID")
            if not raw_id:
                continue
            raw_id = raw_id.strip()
            tid = f"#{raw_id}" if not raw_id.startswith("#") else raw_id

            name = self.get_value_by_header(row, "Name of tool") or ""
            short_desc = self.get_value_by_header(row, "Short description") or ""
            sectors = self.get_obj_sectors(row)

            func_val = self.get_value_by_header(
                row, "27. Functionality_Number of adaptation support cycle steps"
            )
            functionality = None
            if func_val and str(func_val).strip().isdigit():
                functionality = int(str(func_val).strip())

            def is_y(hdr):
                v = self.get_value_by_header(row, hdr)
                return bool(v and v.strip().upper() == "Y")

            tool_data = {
                "external_id": tid,
                "name": name.strip(),
                "short_description": short_desc.strip(),
                "sectors": sectors,
                "climate_impacts": self.get_obj_climateimpacts(row),
                "spatial_resolution": self.get_value_by_header(
                    row, "21. Spatial resolution_Free text (Local, NUTS3, NUTS2…)"
                )
                or "",
                "underlying_data_maintenance": self.get_value_by_header(
                    row, "22. Underlying data maintenance_Free text"
                )
                or "",
                "nature_based_solution": is_y("23. Nature-based solution_Check (Y/N)"),
                "just_resilience": is_y("24. Just resilience_Check (Y/N)"),
                "cost_benefit_ratio": is_y("25. Cost-benefit ratio_Check (Y/N)"),
                "functionality": functionality,
                "strengths_and_possible_limitations": self.get_value_by_header(
                    row,
                    "28. Strengths and possible limitations of the tool_Free text",
                )
                or "",
                "tool_provider": self.get_value_by_header(row, "Tool provider") or "",
                "public_private_mode": self.get_value_by_header(row, "public/private")
                or "",
                "contact": self.get_value_by_header(row, "Contact (person / email)")
                or "",
                "hyperlink": self.get_value_by_header(row, "Tool hyperlink") or "",
                "coder_1": self.get_value_by_header(row, "CODER 1") or "",
                "coder_2": self.get_value_by_header(row, "CODER 1_CODER 2") or "",
                "intended_user_groups": self.get_obj_intended_user_groups(row),
                "place_of_implementation": self.get_obj_place_of_implementation(row),
                "type_of_data": self.get_obj_type_of_data(row),
                "data_sources": self.get_obj_data_sources(row),
                "license_status": self.get_obj_license_status(row),
                "adaptation_support_cycle_step": self.get_obj_adaptation_support_cycle_step(
                    row
                ),
                "tool_available_english": is_y(
                    "18. In which language(s) is the tool available?_English"
                ),
                "tool_available_language": self.get_value_by_header(
                    row,
                    "18. In which language(s) is the tool available?_Other EU/EEA member/cooperating country language",
                )
                or "",
                "type_of_outputs": self.get_obj_type_of_outputs(row),
                "temporality_of_data": self.get_obj_temporality_of_data(row),
                "user_support_provisions": self.get_obj_user_support_provisions(row),
                "tool_validation_use": self.get_obj_tool_validation_use(row),
                "number_of_users_tool": self.get_obj_number_of_users_tool(row),
                "tool_provider_mode": self.get_obj_tool_provider_mode(row),
                "only_interactive_support_tool": is_y(
                    "1. Only *online* interactive support tool"
                ),
                "adaptation_cycle_step": is_y("2. Supports ≥1 adaptation cycle step"),
                "updating_cycle_of_the_tool": is_y(
                    "3. Updating cycle of the tool (Tools <5 years and up to date)"
                ),
                "language_accessibility": is_y("4. Language Accessibility (EEA)"),
                "free_access": is_y("5. Free [full or core functionality] access"),
                "accessibility_and_usability": self.get_obj_tool_accessibility_and_usability(
                    row
                ),
                "geographic_scope": self.get_value_by_header(
                    row, "Geographic coverage/scope"
                )
                or "",
                "include_in_navigator": True,
            }
            tools[tid] = tool_data
        return tools

    def parse_file2_rows(self, rows):
        """Parse extra fields rows from File 2 (ODS rows with multi-row bullets)."""
        if len(rows) < 3:
            return {}

        tools = {}
        cur_id = None
        for row in rows[2:]:
            r = (row + [""] * 8)[:8]
            raw_id = r[0].strip()
            if raw_id:
                tid = f"#{raw_id}" if not raw_id.startswith("#") else raw_id
                cur_id = tid
                tools[cur_id] = {
                    "external_id": cur_id,
                    "name": r[1].strip(),
                    "short_description": r[2].strip(),
                    "inputs": [r[3]] if r[3].strip() else [],
                    "outputs": [r[4]] if r[4].strip() else [],
                    "use_it_to": [r[5]] if r[5].strip() else [],
                    "relevance": [r[6]] if r[6].strip() else [],
                    "used_in": [r[7]] if r[7].strip() else [],
                }
            elif cur_id:
                if r[3].strip():
                    tools[cur_id]["inputs"].append(r[3])
                if r[4].strip():
                    tools[cur_id]["outputs"].append(r[4])
                if r[5].strip():
                    tools[cur_id]["use_it_to"].append(r[5])
                if r[6].strip():
                    tools[cur_id]["relevance"].append(r[6])
                if r[7].strip():
                    tools[cur_id]["used_in"].append(r[7])

        cleaned_extra = {}
        for tid, data in tools.items():
            cleaned_extra[tid] = {
                "name": data["name"],
                "short_description": data["short_description"],
                "inputs_bullets": split_bullets(data["inputs"]),
                "outputs_bullets": split_bullets(data["outputs"]),
                "use_it_to_bullets": split_bullets(data["use_it_to"]),
                "relevance_text": " ".join(
                    [x.strip() for x in data["relevance"] if x.strip()]
                ),
                "used_in_bullets": split_bullets(data["used_in"]),
            }
        return cleaned_extra

    def merge_datasets(self, tools1, tools2):
        """Merge File 1 metadata and File 2 extra fields into unified tool dicts."""
        all_ids = set(tools1.keys()) | set(tools2.keys())
        merged = {}
        for tid in all_ids:
            item = {}
            t1 = tools1.get(tid, {})
            t2 = tools2.get(tid, {})

            item.update(t1)
            item["external_id"] = tid

            if not item.get("name") and t2.get("name"):
                item["name"] = t2["name"]
            if not item.get("short_description") and t2.get("short_description"):
                item["short_description"] = t2["short_description"]

            # Extra rich text fields from File 2
            item["tool_input_bullets"] = t2.get("inputs_bullets", [])
            item["tool_output_bullets"] = t2.get("outputs_bullets", [])
            item["use_it_to_bullets"] = t2.get("use_it_to_bullets", [])
            item["relevance_text"] = t2.get("relevance_text", "")
            item["used_in_bullets"] = t2.get("used_in_bullets", [])

            merged[tid] = item
        return merged

    def find_or_create_tool(self, container, tool_data, existing_map, dry_run=False):
        """Find existing tool by external_id or title, or create new extendedtool."""
        tid = tool_data["external_id"]
        obj = existing_map.get(tid)

        if not obj:
            name_lower = tool_data.get("name", "").strip().lower()
            for ext_id, existing_obj in existing_map.items():
                if existing_obj.Title().strip().lower() == name_lower:
                    obj = existing_obj
                    break

        created = False
        if not obj:
            if dry_run:
                logger.info(
                    "[DRY-RUN] Would CREATE extendedtool: %s -> %s",
                    tid,
                    tool_data.get("name"),
                )
                return None, True
            sectors = tool_data.get("sectors") or ["NONSPECIFIC"]
            impacts = tool_data.get("climate_impacts") or ["NONSPECIFIC"]
            obj = api.content.create(
                container=container,
                type="eea.climateadapt.extendedtool",
                portal_type="eea.climateadapt.extendedtool",
                sectors=sectors,
                climate_impacts=impacts,
                publication_date=date(2026, 1, 1),
                title=tool_data.get("name") or tid,
                external_id=tid,
                safe_id=True,
            )
            obj.external_id = tid
            created = True
            existing_map[tid] = obj
            logger.info("CREATED extendedtool: %s -> %s", tid, tool_data.get("name"))

        return obj, created

    def apply_tool_fields(self, obj, tool_data):
        """Populate all fields on an extendedtool object."""
        tid = tool_data["external_id"]
        obj.external_id = tid

        if tool_data.get("name"):
            obj.title = tool_data["name"]

        if tool_data.get("short_description"):
            obj.long_description = RichTextValue(
                raw=f"<p>{html.escape(tool_data['short_description'])}</p>",
                mimeType="text/html",
                outputMimeType="text/html",
            )

        if "sectors" in tool_data and tool_data["sectors"]:
            obj.sectors = tool_data["sectors"]
        if "climate_impacts" in tool_data and tool_data["climate_impacts"]:
            obj.climate_impacts = tool_data["climate_impacts"]
        if "spatial_resolution" in tool_data:
            obj.spatial_resolution = tool_data["spatial_resolution"]
        if "underlying_data_maintenance" in tool_data:
            obj.underlying_data_maintenance = tool_data["underlying_data_maintenance"]
        if "nature_based_solution" in tool_data:
            obj.nature_based_solution = tool_data["nature_based_solution"]
        if "just_resilience" in tool_data:
            obj.just_resilience = tool_data["just_resilience"]
        if "cost_benefit_ratio" in tool_data:
            obj.cost_benefit_ratio = tool_data["cost_benefit_ratio"]
        if "functionality" in tool_data:
            obj.functionality = tool_data["functionality"]
        if "strengths_and_possible_limitations" in tool_data:
            obj.strengths_and_possible_limitations = tool_data[
                "strengths_and_possible_limitations"
            ]
        if "tool_provider" in tool_data:
            obj.tool_provider = tool_data["tool_provider"]
        if "public_private_mode" in tool_data:
            obj.public_private_mode = tool_data["public_private_mode"]
        if "contact" in tool_data:
            obj.contact = tool_data["contact"]
        if "hyperlink" in tool_data:
            obj.hyperlink = tool_data["hyperlink"]
        if "coder_1" in tool_data:
            obj.coder_1 = tool_data["coder_1"]
        if "coder_2" in tool_data:
            obj.coder_2 = tool_data["coder_2"]
        if "intended_user_groups" in tool_data:
            obj.intended_user_groups = tool_data["intended_user_groups"]
        if "place_of_implementation" in tool_data:
            obj.place_of_implementation = tool_data["place_of_implementation"]
        if "type_of_data" in tool_data:
            obj.type_of_data = tool_data["type_of_data"]
        if "data_sources" in tool_data:
            obj.data_sources = tool_data["data_sources"]
        if "license_status" in tool_data:
            obj.license_status = tool_data["license_status"]
        if "adaptation_support_cycle_step" in tool_data:
            obj.adaptation_support_cycle_step = tool_data[
                "adaptation_support_cycle_step"
            ]
        if "tool_available_english" in tool_data:
            obj.tool_available_english = tool_data["tool_available_english"]
        if "tool_available_language" in tool_data:
            obj.tool_available_language = tool_data["tool_available_language"]
        if "type_of_outputs" in tool_data:
            obj.type_of_outputs = tool_data["type_of_outputs"]
        if "temporality_of_data" in tool_data:
            obj.temporality_of_data = tool_data["temporality_of_data"]
        if "user_support_provisions" in tool_data:
            obj.user_support_provisions = tool_data["user_support_provisions"]
        if "tool_validation_use" in tool_data:
            obj.tool_validation_use = tool_data["tool_validation_use"]
        if "number_of_users_tool" in tool_data:
            obj.number_of_users_tool = tool_data["number_of_users_tool"]
        if "tool_provider_mode" in tool_data:
            obj.tool_provider_mode = tool_data["tool_provider_mode"]
        if "only_interactive_support_tool" in tool_data:
            obj.only_interactive_support_tool = tool_data[
                "only_interactive_support_tool"
            ]
        if "adaptation_cycle_step" in tool_data:
            obj.adaptation_cycle_step = tool_data["adaptation_cycle_step"]
        if "updating_cycle_of_the_tool" in tool_data:
            obj.updating_cycle_of_the_tool = tool_data["updating_cycle_of_the_tool"]
        if "language_accessibility" in tool_data:
            obj.language_accessibility = tool_data["language_accessibility"]
        if "free_access" in tool_data:
            obj.free_access = tool_data["free_access"]
        if "accessibility_and_usability" in tool_data:
            obj.accessibility_and_usability = tool_data["accessibility_and_usability"]
        if "include_in_navigator" in tool_data:
            obj.include_in_navigator = tool_data["include_in_navigator"]

        # Geographic scope
        if "geographic_scope" in tool_data and tool_data["geographic_scope"]:
            (
                is_global,
                country_names,
                country_codes,
                subnational_key,
                macro_regions,
                city,
            ) = self.process_region(tool_data["geographic_scope"])
            try:
                raw_geochars = getattr(obj, "geochars", None)
                if isinstance(raw_geochars, bytes):
                    raw_geochars = raw_geochars.decode("utf-8")
                geochars = json.loads(raw_geochars or "{}")
            except Exception:
                geochars = {}
            if "geoElements" not in geochars:
                geochars["geoElements"] = {}
            geochars["geoElements"]["element"] = is_global.upper()
            if macro_regions:
                geochars["geoElements"]["macrotrans"] = macro_regions
            if country_codes:
                geochars["geoElements"]["countries"] = country_codes
            if subnational_key:
                geochars["geoElements"]["subnational"] = [subnational_key]
            else:
                geochars["geoElements"]["subnational"] = []
            if city:
                geochars["geoElements"]["city"] = city
            elif "city" not in geochars["geoElements"]:
                geochars["geoElements"]["city"] = ""
            obj.geochars = json.dumps(geochars)

        # Extra rich text fields from File 2
        if tool_data.get("tool_input_bullets"):
            obj.tool_input = to_richtext_list(tool_data["tool_input_bullets"])
        if tool_data.get("tool_output_bullets"):
            obj.tool_output = to_richtext_list(tool_data["tool_output_bullets"])
        if tool_data.get("use_it_to_bullets"):
            obj.use_it_to = to_richtext_list(tool_data["use_it_to_bullets"])
        if tool_data.get("relevance_text"):
            obj.climate_adaptation_relevance = to_richtext_text(
                tool_data["relevance_text"]
            )
        if tool_data.get("used_in_bullets"):
            obj.used_in = to_richtext_list(tool_data["used_in_bullets"])

        obj._p_changed = True
        obj.reindexObject()

    def import_tools(self, site, merged_tools, dry_run=True, container=None):
        """Import all merged tools into the portal.

        :param site: Plone portal object
        :param merged_tools: dict of tool data keyed by tool id
        :param dry_run: bool, if True do not commit changes
        :param container: target container object or path (default: /cca/en/metadata/tools)
        """
        if container is None:
            container = api.content.get(path="/cca/en/metadata/tools")
            if not container and hasattr(site, "unrestrictedTraverse"):
                container = site.unrestrictedTraverse("en/metadata/tools", None)
            if not container:
                raise RuntimeError("Folder /cca/en/metadata/tools not found!")
        elif isinstance(container, str):
            target_path = container
            container = api.content.get(path=target_path)
            if not container and hasattr(site, "unrestrictedTraverse"):
                container = site.unrestrictedTraverse(target_path.lstrip("/"), None)
            if not container:
                raise RuntimeError(f"Folder {target_path} not found!")
        else:
            from Products.CMFPlone.interfaces import IPloneSiteRoot

            if IPloneSiteRoot.providedBy(container):
                default_c = api.content.get(path="/cca/en/metadata/tools")
                if not default_c and hasattr(site, "unrestrictedTraverse"):
                    default_c = site.unrestrictedTraverse("en/metadata/tools", None)
                if default_c:
                    container = default_c
            else:
                from plone.dexterity.interfaces import IDexterityContainer
                from Products.CMFCore.interfaces import IFolderish

                if not IFolderish.providedBy(
                    container
                ) and not IDexterityContainer.providedBy(container):
                    parent = getattr(container, "aq_parent", None)
                    if parent is not None and (
                        IFolderish.providedBy(parent)
                        or IDexterityContainer.providedBy(parent)
                    ):
                        container = parent

        container_path = (
            "/".join(container.getPhysicalPath())
            if hasattr(container, "getPhysicalPath")
            else str(container)
        )
        logger.info("Target import container: %s (dry_run=%s)", container_path, dry_run)

        if not dry_run:
            try:
                from plone.base.interfaces.constrains import ISelectableConstrainTypes
            except ImportError:
                from Products.CMFPlone.interfaces.constrains import (
                    ISelectableConstrainTypes,
                )
            aspect = ISelectableConstrainTypes(container, None)
            if aspect:
                allowed = list(aspect.getLocallyAllowedTypes())
                if "eea.climateadapt.extendedtool" not in allowed:
                    allowed.append("eea.climateadapt.extendedtool")
                    aspect.setLocallyAllowedTypes(allowed)
                    aspect.setImmediatelyAddableTypes(allowed)

        existing_map = {}
        for id_name, child in container.objectItems():
            ext_id = getattr(child, "external_id", None)
            if ext_id:
                existing_map[ext_id] = child

        results = []
        i = 0
        created_count = 0
        updated_count = 0

        for tid in sorted(
            merged_tools.keys(),
            key=lambda x: int(x[1:]) if x[1:].isdigit() else 99999,
        ):
            tool_data = merged_tools[tid]
            obj, created = self.find_or_create_tool(
                container, tool_data, existing_map, dry_run=dry_run
            )

            if dry_run:
                if created:
                    created_count += 1
                else:
                    updated_count += 1
                results.append(
                    {
                        "external_id": tid,
                        "name": tool_data.get("name", ""),
                        "url": "DRY_RUN",
                        "status": "CREATED" if created else "UPDATED",
                        "inputs": len(tool_data.get("tool_input_bullets", [])),
                        "outputs": len(tool_data.get("tool_output_bullets", [])),
                        "use_it_to": len(tool_data.get("use_it_to_bullets", [])),
                        "relevance": bool(tool_data.get("relevance_text")),
                        "used_in": len(tool_data.get("used_in_bullets", [])),
                    }
                )
                continue

            self.apply_tool_fields(obj, tool_data)
            if created:
                created_count += 1
            else:
                updated_count += 1

            results.append(
                {
                    "external_id": tid,
                    "name": tool_data.get("name", ""),
                    "url": obj.absolute_url(),
                    "status": "CREATED" if created else "UPDATED",
                }
            )

            i += 1
            if i % 20 == 0:
                transaction.savepoint()

        if not dry_run:
            transaction.commit()

        logger.info(
            "IMPORT COMPLETED: %d total tools (%d created, %d updated, dry_run=%s)",
            len(results),
            created_count,
            updated_count,
            dry_run,
        )
        return results

    def run_web_import(self, file1_upload=None, file2_upload=None, context=None):
        """Adapter for browser migration view upload form."""
        if not file1_upload and not file2_upload:
            return []

        tools1 = {}
        if file1_upload:
            if hasattr(file1_upload, "read"):
                content = file1_upload.read()
            else:
                content = file1_upload
            if content and len(content) > 0:
                if content.startswith(b"PK"):
                    rows = parse_ods_rows(content)
                else:
                    import csv

                    csv_text = content.decode("utf-8", errors="replace")
                    reader = csv.reader(io.StringIO(csv_text))
                    rows = list(reader)
                tools1 = self.parse_file1_rows(rows)

        tools2 = {}
        if file2_upload:
            if hasattr(file2_upload, "read"):
                content2 = file2_upload.read()
            else:
                content2 = file2_upload
            if content2 and len(content2) > 0:
                rows2 = parse_ods_rows(content2)
                tools2 = self.parse_file2_rows(rows2)

        if not tools1 and not tools2:
            return []

        merged = self.merge_datasets(tools1, tools2)
        site = api.portal.get()
        return self.import_tools(site, merged, dry_run=False, container=context)
