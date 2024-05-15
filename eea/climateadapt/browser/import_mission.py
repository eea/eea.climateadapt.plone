import csv
from copy import deepcopy

from eea.climateadapt.vocabulary import ace_countries
from pkg_resources import resource_filename
from plone.api.content import create
from plone.app.textfield.value import RichTextValue
from Products.Five.browser import BrowserView

_ace_countries = ace_countries + [
    ("MD", "Moldova"),
    ("MK", "North Macedonia"),
    ("XK", "Kosovo"),
    ("NZ", "New Zealand"),
    ("TN", "Tunisia"),
    ("DZ", "Algeria"),
    ("LB", "Lebanon"),
    ("JO", "Jordan"),
    # ('Country not found:', 'New Zealand')
    # ('Country not found:', 'Tunisia')
    # ('Country not found:', 'T\xc3\xbcrkiye')
    # ('Country not found:', 'Liechtenstein and Norway')
    # ('Country not found:', 'Palestine')
    # ('Country not found:', 'Norway and Switzerland')
    # ('Country not found:', 'EEA')
]
ace_countries_mapping = {}
for k, v in _ace_countries:
    ace_countries_mapping[v] = k

EU27 = [
    "Austria",
    "Belgium",
    "Bulgaria",
    "Croatia",
    "Cyprus",
    "Czechia",
    "Denmark",
    "Estonia",
    "Finland",
    "France",
    "Germany",
    "Greece",
    "Hungary",
    "Ireland",
    "Italy",
    "Latvia",
    "Lithuania",
    "Luxembourg",
    "Malta",
    "Netherlands",
    "Poland",
    "Portugal",
    "Romania",
    "Slovakia",
    "Slovenia",
    "Spain",
    "Sweden",
]

EEA = EU27 + ["Iceland", "Liechtenstein", "Norway"]

eu_countries = ", ".join(EU27)
eea_countries = ", ".join(EEA)

sectors_map = {
    "Agriculture": "AGRICULTURE",
    "Buildings": "BUILDINGS",
    "Disaster Risk Reduction": "DISASTERRISKREDUCTION",
    "Forestry": "FORESTRY",
    "Health": "HEALTH",
    "Transport": "TRANSPORT",
    "Water management": "WATERMANAGEMENT",
    "Energy": "ENERGY",
    "Tourism": "TOURISMSECTOR",
    "Biodiversity protection": "BIODIVERSITY",
    "Biodiversity": "BIODIVERSITY",
    "Coastal Areas": "COASTAL",
    "Ecosystems restoration": "NONSPECIFIC",
    "Marine and Fisheries": "MARINE",
    # "Other": "NONSPECIFIC",
    "Other": None,
}

ast_map = {
    "AST 1: Preparing the ground for adaptation": "AST_STEP_1",
    "AST 2: Assessing risks and vulnerability to climate change": "AST_STEP_2",
    "AST 3: Identifying adaptation options": "AST_STEP_3",
    "AST 4: Assessing adaptation options": "AST_STEP_4",
    "AST 5: Implementation": "AST_STEP_5",
    "AST 6: Monitoring & Evaluation (M&E)": "AST_STEP_6",
}

LABEL_INDEX = 2
START_INDEX = 3


def tobool(value):
    if value == "YES":
        return True
    elif value == "NO":
        return False
    return None


def text(column):
    def convert(row, data):
        value = row[column].strip()
        return value

    return convert


def choices(columns, value_map=None):
    def convert(row, data):
        value = []
        cells = data[LABEL_INDEX][columns[0] : columns[-1] + 1]
        labels = [cell.strip() for cell in cells]

        for i, col in enumerate(columns):
            val = row[col].strip()
            if tobool(val):
                if value_map:
                    mapped = value_map[labels[i]]
                    if mapped:
                        value.append(mapped)
                else:
                    value.append(labels[i])

        return value

    return convert


def boolean_field(column):
    def convert(row, data):
        value = row[column].strip()
        return tobool(value)

    return convert


def richtext(column):
    def convert(row, data):
        value = row[column].strip()
        # TODO: use inteligent text converter
        return RichTextValue(unicode("<p>%s</p>") % value.decode("utf-8"))

    return convert


def richtext_links(column):
    def convert(row, data):
        out = []

        for label_col, link_col in column:
            label = row[label_col].strip()
            link = row[link_col].strip()
            out.append((link, label))

        # returns pairs of (link, label)
        return out

    return convert


def country_field(column_a):
    def convert(row, data):
        value = row[column_a].strip()
        replacements = {
            "EU-27": eu_countries,
            ".": " ",
            "Moldavia": "Moldova",
            "T\xc3\xbcrkiye": "Turkey",
            "Liechtenstein and Norway": "Liechtenstein, Norway",
            "Norway and Switzerland": "Norway, Switzerland",
            "EEA": eea_countries,
        }
        # value = value.replace().replace(".", " ")
        for k, v in replacements.items():
            value = value.replace(k, v)
        out = []
        for cname in value.split(","):
            cname = cname.strip()
            if cname not in ace_countries_mapping:
                print("Country not found:", cname)
                continue
            out.append(ace_countries_mapping[cname])

        return sorted(list(set(out)))

    return convert


class MissionFundingImporter(BrowserView):
    """Import mission funding items from CSV"""

    def set_nonmetadata_fields(self, obj, fields):
        blocks_copy = deepcopy(obj.blocks)
        blocks_layout = obj.blocks_layout["items"]

        columnblock = None
        for uid in blocks_layout:
            block = blocks_copy[uid]
            if block["@type"] == "columnsBlock":
                columnblock = block

        firstcol_id = columnblock["data"]["blocks_layout"]["items"][0]
        firstcol = columnblock["data"]["blocks"][firstcol_id]

        for i, block_id in enumerate(firstcol["blocks_layout"]["items"]):
            nextuid = None
            if i < len(firstcol["blocks_layout"]["items"]) - 1:
                nextuid = firstcol["blocks_layout"]["items"][i + 1]
            blocks = firstcol["blocks"]
            block = blocks[block_id]
            text = block.get("plaintext", "")

            if "Objective of the funding programme" in text:
                blocks[nextuid] = self.text2slate(fields["objective"])

            if "Funding rate (percentage of covered costs)" in text:
                blocks[nextuid] = self.text2slate(fields["funding_rate"])

            if "Administering authority" in text:
                blocks[nextuid] = self.text2slate(fields["authority"])

            if "Publication page" in text:
                linksblock = self.links2slate(fields["publication_page"])
                blocks[nextuid] = linksblock

            if "General information" in text:
                blocks[nextuid] = self.maybe_link(fields["general_info"])

            if "Further information" in text:
                blocks[nextuid] = self.maybe_link(fields["further_info"])

            if block["@type"] == "metadata":
                if block["data"]["id"] == "is_consortium_required":
                    blocks[nextuid] = self.text2slate(fields["yes_consortium"])
                if block["data"]["id"] == "funding_type":
                    blocks[nextuid] = self.text2slate(fields["funding_type_other"])

        return blocks_copy

    def maybe_link(self, text):
        if text.startswith("http"):
            return {
                "@type": "slate",
                "plaintext": text,
                "value": [
                    {
                        "type": "p",
                        "children": [
                            {"text": ""},
                            {
                                "type": "link",
                                "data": {"url": text},
                                "children": [{"text": "External link"}],
                            },
                            {"text": ""},
                        ],
                    }
                ],
            }
        else:
            return self.text2slate(text)

    def links2slate(self, links):
        text = "\n".join([bits[1] for bits in links])
        children = [{"text": ""}]

        for link, label in links:
            if link.strip() == "0":
                if label.strip() == "0":
                    continue

                children.extend([{"text": label}, {"text": "\n"}])
                continue

            el = {"type": "link", "data": {"url": link}, "children": [{"text": label}]}
            children.extend([el, {"text": "\n"}])

        return {
            "@type": "slate",
            "plaintext": text,
            "value": [{"children": children, "type": "p"}],
        }

    def text2slate(self, text):
        children = [{"text": ""}]

        if text.strip() not in ["0", "NO"]:
            children += [{"text": text}, {"text": ""}]

        return {
            "@type": "slate",
            "plaintext": text,
            "value": [{"children": children, "type": "p"}],
        }

    def __call__(self):
        # metarow_index = 1
        # these are 0-based indexes
        fields_definition = dict(
            title=text(2),
            is_blended=boolean_field(44),
            is_consortium_required=boolean_field(45),
            country=country_field(4),
            funding_type=choices([31, 32, 33, 34]),
            budget_range=choices([36, 37, 38, 39, 40]),
            rast_steps=choices([8, 9, 10, 11, 12, 13], ast_map),
            eligible_entities=choices([14, 15, 16, 17]),
            sectors=choices(
                [18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29],
                sectors_map,  # , 30, 31
            ),
            regions=richtext(6),
        )

        nonmetadata_fields = dict(
            objective=text(50),  # done
            funding_type_other=text(35),  # done
            funding_rate=text(41),  # done
            further_info=text(74),  # done
            general_info=text(3),  # done
            authority=text(52),  # done
            yes_consortium=text(46),  # done
            # these are a lot of links 60-69
            publication_page=richtext_links(
                [[59, 60], [61, 62], [63, 64], [65, 66], [67, 68]]
            ),
        )

        fpath = resource_filename(
            "eea.climateadapt.browser", "data/mission_funding.csv"
        )
        toimport = []
        with open(fpath) as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            wholedata = list(reader)
            for row in wholedata[START_INDEX:]:
                record = {}
                nonmetadata_record = {}

                for name, converter in fields_definition.items():
                    value = converter(row, wholedata)
                    record[name] = value

                for name, converter in nonmetadata_fields.items():
                    value = converter(row, wholedata)
                    nonmetadata_record[name] = value

                toimport.append((record, nonmetadata_record))

        printed = []

        for record, nonmetadata_record in toimport:
            obj = create(type="mission_funding_cca", container=self.context, **record)
            blocks = self.set_nonmetadata_fields(obj, nonmetadata_record)
            obj.blocks = blocks
            obj._p_changed = True
            url = obj.absolute_url()
            print("Imported %s" % url)
            printed.append(url)

        return str(printed)
