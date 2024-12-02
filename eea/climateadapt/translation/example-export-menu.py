menu = """
About
    About Climate-ADAPT            /about
    Outreach & dissemination       /about/outreach-and-dissemination
         -Dissemination materials              /about/outreach-and-dissemination/dissemination-materials
         -Tutorial videos                      /about/outreach-and-dissemination/tutorial-videos
         -Inspiring Climate-ADAPT use cases    /about/outreach-and-dissemination/inspiring-climate-adapt-use-cases
         - Climate-ADAPT performance reporting /about/outreach-and-dissemination/climate-adapt-performance-reporting
         - Climate-ADAPT events and webinars   /about/outreach-and-dissemination/climate-adapt-events-and-webinars
         - Country specific promotions         /about/outreach-and-dissemination/country-specific-climate-adapt-promotion-activities
    Site map                       /sitemap

EU policy
    EU ADAPTATION POLICY
        -EU Adaptation Strategy              /eu-adaptation-policy/strategy
        -EU Mission on Adaptation            /eu-adaptation-policy/eu-mission-on-adaptation
        -EU Reporting on Adaptation          /eu-adaptation-policy/eu-adaptation-reporting-mmr
        -EU Covenant of Mayors               /eu-adaptation-policy/covenant-of-mayors
        -EU Sustainable Finance Strategy     /eu-adaptation-policy/eu-sustainable-finance-strategy/
        -EU funding of adaptation            /eu-adaptation-policy/funding
    ADAPTATION IN EU POLICY SECTORS          /eu-adaptation-policy/sector-policies
        -Agriculture                         /eu-adaptation-policy/sector-policies/agriculture
        -Biodiversity                        /eu-adaptation-policy/sector-policies/biodiversity
        -Buildings                           /eu-adaptation-policy/sector-policies/buildings
        -Coastal areas                       /eu-adaptation-policy/sector-policies/coastal-areas
        -Disaster risk reduction             /eu-adaptation-policy/sector-policies/disaster-risk-reduction
        -Ecosystem-based approaches          /eu-adaptation-policy/sector-policies/ecosystem
        -Energy                              /eu-adaptation-policy/sector-policies/energy
        -Financial                           /eu-adaptation-policy/sector-policies/financial
        -Forestry                            /eu-adaptation-policy/sector-policies/forestry
        -Health                              /eu-adaptation-policy/sector-policies/health
        -Marine and fisheries                /eu-adaptation-policy/sector-policies/marine-and-fisheries
        -Transport                           /eu-adaptation-policy/sector-policies/transport
        -Urban                               /eu-adaptation-policy/sector-policies/urban
        -Water management                    /eu-adaptation-policy/sector-policies/water-management
    EU REGIONAL POLICY                       /other-eu-policies/eu-regional-policy

Countries, Transnational regions, Cities              /countries-regions
Country Profiles               /countries-regions/countries
Cities and towns               /eu-adaptation-policy/sector-policies/urban
Transnational regions                                 /countries-regions/transnational-regions
        -Adriatic-Ionian                              /countries-regions/transnational-regions/adriatic-ionian
        -Alpine Space                                 /countries-regions/transnational-regions/alpine-space
        -Atlantic Area                                /countries-regions/transnational-regions/atlantic-area
        -Balkan-Mediterranean                         /countries-regions/transnational-regions/balkan-mediterranean
        -Baltic Sea                                   /countries-regions/transnational-regions/baltic-sea-region
        -Central Europe                               /countries-regions/transnational-regions/central-europe
        -Danube                                       /countries-regions/transnational-regions/danube
        -Mediterranean                                /countries-regions/transnational-regions/mediterranean
        -North Sea                                    /countries-regions/transnational-regions/north-sea
        -North West Europe                            /countries-regions/transnational-regions/north-west-europe
        -Northern Periphery and Arctic                /countries-regions/transnational-regions/northern-periphery
        -South West Europe                            /countries-regions/transnational-regions/south-west-europe
        -Other regions                                /countries-regions/transnational-regions/other-regions

Knowledge
    TOPICS
        -Impacts, risks and vulnerabilities                   /knowledge/adaptation-information/vulnerabilities-and-risks
        -Adaptation options                                   /knowledge/adaptation-information/adaptation-measures
        -Uncertainty guidance                                 /knowledge/tools/uncertainty-guidance
        -Monitoring, Reporting and Evaluation                 /knowledge/mre
        -Europe's vulnerability to climate change impacts occurring outside Europe   /knowledge/eu-vulnerability/eu-vulnerability-to-cc-impacts-occurring-outside/
    DATA AND INDICATORS
        - Climate  Services                                   /knowledge/adaptation-information/climate-services/
        -Indicators in Climate-ADAPT                          /knowledge/c-a-indicators
    RESEARCH AND INNOVATION PROJECTS                          /knowledge/adaptation-information/research-projects
    EUROPEAN CLIMATE DATA EXPLORER                            /knowledge/european-climate-data-explorer/
    ---
    TOOLS
        -Adaptation Support Tool                              /knowledge/tools/adaptation-support-tool
        -Urban Adaptation Support Tool                        /knowledge/tools/urban-ast/step-0-0
        -Urban Adaptation Map Viewer                          /knowledge/tools/urban-adaptation
        -Economic tools                                       /knowledge/tools/economic-tools
    PRACTICE
        -Case study explorer                                 /knowledge/tools/case-study-explorer
        -Case studies                                         /knowledge/tools/case-studies-climate-adapt/
        -LIFE projects                                        /knowledge/life-projects
        -INTERREG projects                                    /knowledge/interreg-projects
        -Climate-ADAPT use cases                              /knowledge/climate-adapt-use-cases
        [<icon class="fa fa-database">]Search the database    /data-and-downloads
    EUROPEAN Climate and Health Observatory                   /observatory

Networks                /network/organisations

Help                                        /help
    Glossary                                /help/glossary
    FAQ for users                           /help/faq
    FAQ for providers                       /help/faq-providers
    Guidance to search function             /help/guidance
    Tutorial Videos                         /help/tutorial-videos
    Webinars                                /help/Webinars
    Share your information                  /help/share-your-info/general
"""

import re

from babel._compat import BytesIO
from babel.messages import Catalog
from babel.messages.pofile import write_po

icon_re = re.compile("\[.*\]")


def export_po(text, location_name="menu", domain="cca_menu"):
    catalog = Catalog(domain=domain)
    buf = BytesIO()

    for (i, line) in enumerate(text.split("\n")):
        # print(line)
        line = line.strip()
        if not line:
            continue
        if line.startswith("--"):
            continue
        if line.startswith("-"):
            line = line[1:].strip()
        if "/" in line:
            b0, b1 = line.split("/", 1)
        else:
            b0 = line

        msg = icon_re.sub("", b0)
        msg = msg.strip()

        catalog.add(msg, locations=[(location_name, i)])

    write_po(buf, catalog, omit_header=False)
    return buf.getvalue().decode("utf8")


if __name__ == "__main__":
    print((export_po(menu)))
