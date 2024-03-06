IGNORED_CONTENT_TYPES = [
    # TODO:
    # 'Document',
    # 'Event',
    # 'News Item',
    "cca-event",
    "eea.climateadapt.aceproject",
    "eea.climateadapt.adaptationoption",
    "eea.climateadapt.c3sindicator",
    "eea.climateadapt.casestudy",
    "eea.climateadapt.city_profile",
    "eea.climateadapt.guidancedocument",
    "eea.climateadapt.indicator",
    "eea.climateadapt.informationportal",
    "eea.climateadapt.mapgraphdataset",
    "eea.climateadapt.organisation",
    "eea.climateadapt.publicationreport",
    "eea.climateadapt.researchproject",
    "eea.climateadapt.tool",
    "eea.climateadapt.video",
    "Image",
    "LRF",
    "LIF",
    "Collection",
    "Link",
    "DepictionTool",
    "Subsite",
    "File",
    "eea.climateadapt.city_profile",
    "FrontpageSlide",
    "EasyForm",
]

LANGUAGES = ["de", "fr", "es", "it", "pl", "en"]


IGNORED_PATHS = [
    "{lang}/mission",
    "{lang}/metadata" "frontpage",
    "{lang}/frontpage",
    # "{lang}/observatory/news-archive-observatory",
]

COL_MAPPING = {
    2: "oneThird",
    3: "oneThird",
    4: "oneThird",
    5: "oneThird",
    6: "halfWidth",
    7: "twoThirds",
    8: "twoThirds",
    9: "twoThirds",
    10: "twoThirds",
    12: "full",
}

TOP_LEVEL = {
    "/en/about": [],
    "/en/eu-adaptation-policy": [],
    "/en/countries-regions": [],
    "/en/knowledge": [],
    "/en/network": [],
}

AST_PATHS = ["/knowledge/tools/urban-ast",
             "/knowledge/tools/adaptation-support-tool"]

FULL_PAGE_PATHS = ["/observatory", "/knowledge/forestry"]

SECTOR_POLICY_PATHS = [
    "/eu-adaptation-policy/sector-policies/agriculture",
    "/eu-adaptation-policy/sector-policies/biodiversity",
    "/eu-adaptation-policy/sector-policies/buildings",
    "/eu-adaptation-policy/sector-policies/business-and-industry",
    "/eu-adaptation-policy/sector-policies/coastal-areas",
    "/eu-adaptation-policy/sector-policies/cultural-heritage",
    "/eu-adaptation-policy/sector-policies/disaster-risk-reduction",
    "/eu-adaptation-policy/sector-policies/energy",
    "/eu-adaptation-policy/sector-policies/financial",
    "/eu-adaptation-policy/sector-policies/forestry",
    "/eu-adaptation-policy/sector-policies/health",
    "/eu-adaptation-policy/sector-policies/ict/",
    "/eu-adaptation-policy/sector-policies/land-use-planning",
    "/eu-adaptation-policy/sector-policies/marine-and-fisheries",
    "/eu-adaptation-policy/sector-policies/mountain-areas",
    "/eu-adaptation-policy/sector-policies/transport",
    "/eu-adaptation-policy/sector-policies/tourism",
    "/eu-adaptation-policy/sector-policies/urban",
    "/eu-adaptation-policy/sector-policies/water-management",
    "/knowledge/adaptation-information/vulnerabilities-and-risks",
    "/knowledge/adaptation-information/adaptation-measures",
]

SECTOR_POLICIES = [
    (
        "Agriculture",
        "Climate change has complex effects on the bio-physical "
        "processes that underpin agricultural systems, with both negative "
        "and positive consequences in different EU regions. Rising atmospheric "
        "CO2 concentration, higher temperatures, changes in precipitation patterns "
        "and in frequency of extreme events both affect the natural environment as "
        "well as the quantity, quality and stability of food production. Climatic "
        "variations impact on water resources, soils, pests and diseases, leading "
        "to significant changes in agriculture and livestock production.",
        "/eu-adaptation-policy/sector-policies/agriculture",
    ),
    (
        "Biodiversity",
        "Buildings can be vulnerable to climate change. In the future there may be "
        "an increase in the risk of collapse, declining state and significant loss "
        "of value as a result of more storms, snow or subsidence damage, water "
        "encroachment, deteriorating indoor climate and reduced building lifetime. "
        "The European Commission aims to increase the climate resilience of "
        "infrastructure, including buildings. New and existing buildings  need to be "
        "assessed for resilience to current risks and future climate changes, and "
        "planned or upgraded accordingly. A key policy used to support the resilience "
        "of buildings is the Cohesion Policy (also referred to as Regional Policy).",
        "/eu-adaptation-policy/sector-policies/biodiversity",
    ),
    (
        "Buildings",
        "Buildings can be vulnerable to climate change. In the future there may be an "
        "increase in the risk of collapse, declining state and significant loss of "
        "value as a result of more storms, snow or subsidence damage, water encroachment, "
        "deteriorating indoor climate and reduced building lifetime. The European Commission "
        "aims to increase the climate resilience of infrastructure, including buildings. "
        "New and existing buildings  need to be assessed for resilience to current risks "
        "and future climate changes, and planned or upgraded accordingly. A key policy used "
        "to support the resilience of buildings is the Cohesion Policy (also referred to as "
        "Regional Policy).",
        "/eu-adaptation-policy/sector-policies/buildings",
    ),
    (
        "Business and Industry",
        "Firms face two main types of climate-related risks: direct physical risks and "
        "transition risks that arise from society's response to climate change, mainly "
        "mitigation actions.  Climate change can have significant impacts on supply chains, "
        "distribution, and sales in a number of ways. Heat negatively affects human health "
        "and can lead to poorer work performance (reduced productivity) or lower numbers of "
        "hours committed to work (labour supply).",
        "/eu-adaptation-policy/sector-policies/business-and-industry",
    ),
    (
        "Coastal areas",
        "Sea level rise can cause flooding, coastal erosion and the loss of low-lying coastal "
        "systems. It will also increase the risk of storm surges and the likelihood of landward "
        "intrusion of saltwater and may endanger coastal ecosystems. Expected rises in water "
        "temperatures and ocean acidification will contribute to a restructuring of coastal "
        "ecosystems; with implications for ocean circulation and biogeochemical cycling.",
        "/eu-adaptation-policy/sector-policies/coastal-areas",
    ),
    (
        "Cultural Heritage",
        "The impacts of catastrophic events on this heritage are coupled with the slow onset "
        "of changes arising from deterioration processes. Continuous increase in temperature "
        "and fluctuations in temperature and humidity or fluctuations in freeze-thaw cycles "
        "causes degradation and stress in materials, leading to a greater need for restoration "
        "and conservation. Biological degradation caused by microorganisms, for example, are "
        "more likely to occur.",
        "/eu-adaptation-policy/sector-policies/cultural-heritage",
    ),
    (
        "Disaster risk reduction",
        "Over the past few years, Europe has experienced every type of natural disasters: "
        "severe floods, droughts, and forest fires with devastating effects on people's lives, "
        "the European economy and the environment. In the past decade, the European Commission "
        "adopted several strategies and actions to cope with disaster risk reduction as, for "
        "instance, the Floods Directive and its implementation (timetable), the EU Action on "
        "Water Scarcity and Drought, the Green Paper on insurance in the context of natural and "
        "man-made disasters.",
        "/eu-adaptation-policy/sector-policies/disaster-risk-reduction",
    ),
    (
        "Energy",
        "Climate change affects the energy sector in multiple ways, ranging from changes in "
        "heating and cooling demand; to impacts on energy supply conditions - for example "
        "decreased water availability for hydropower during prolonged droughts and reduced "
        "availability of cooling water affecting the efficiency of power plants. Furthermore, "
        "energy infrastructure can be more exposed to damages by changing climate conditions. "
        "The European Commission in general aims to increase the climate resilience of "
        "infrastructure including energy by providing strategical frameworks.",
        "/eu-adaptation-policy/sector-policies/energy",
    ),
    (
        "Financial",
        "Extreme weather events in recent years have increased the urgency to mainstream climate "
        "change adaptation into the different EU policy fields. There are few specific EU "
        "activities to mainstream climate change adaptation into policies for financial and "
        "insurance sectors. However many European policies related to natural disasters "
        "(see Disaster risk reduction) are very relevant to the financial and insurance sector, "
        "as they may help to prevent significant losses and financial disasters. The European "
        "Commission has also committed itself to increasing financing of climate-related "
        "activities by ensuring that at least 20% of the European budget is climate-related "
        "expenditure.",
        "/eu-adaptation-policy/sector-policies/financial",
    ),
    (
        "Forestry",
        "The rapid rate of climate change may overcome the natural ability of forest ecosystems "
        "to adapt. It leads to increased risk of disturbances through storms, fire, pests and "
        "diseases with implications for forest growth and production. The economic viability of "
        "forestry will be affected, mainly in southern areas of Europe, as well as the capacity "
        "of forests to provide environmental services, including changes in the carbon sink "
        "function. In 2013, the Commission adopted a new EU Forest Strategy, which responds to "
        "new challenges facing forests and the forest sector.",
        "/eu-adaptation-policy/sector-policies/forestry",
    ),
    (
        "Health",
        "Climate change will generate new health risks and amplify current health problems. "
        "Both direct and indirect effects on human, plant and animal health are expected from "
        "climate change. Direct effects result from changes in the intensity and frequency of "
        "extreme weather events like heatwaves and floods. Indirect effects can be felt through "
        "changes in the incidence of diseases transmitted by insects (i.e. vector borne diseases "
        "caused by mosquitoes and ticks), rodents, or changes in water, food and air quality. "
        "The European Commission's EU strategy on adaptation to climate change is accompanied by "
        "a Staff Working Document.",
        "/eu-adaptation-policy/sector-policies/health",
    ),
    (
        "ICT",
        "The challenges posed by climate change for the ICT fall into two main categories: acute "
        "events and chronic stresses. Acute events (also termed critical or crisis events) "
        "include floods (pluvial, fluvial, coastal), ice storms, heatwaves, etc. Acute events "
        "compromise ICT infrastructures by destroying or disabling the physical assets that they "
        "depend on. Chronic stresses result from more gradual changes in climate norms, such as "
        "including changes in temperature ranges and humidity levels. While these impacts are less "
        "likely to have catastrophic consequences, they will lead to increased asset degradation, "
        "more frequent failures and shorter life spans.",
        "/eu-adaptation-policy/sector-policies/ict",
    ),
    (
        "Land use planning",
        "Land use planning is identified as one of the most effective processes to facilitate local "
        "adaptation to climate change. Existing processes and tools available through the municipal "
        "land use planning process in the EU, including official plans, zoning, and/or development "
        "permits, assist in minimizing the development risks to a municipality from the predicted "
        "impacts of increased floods, wildfires, landslides, and/or other natural hazards due to a "
        "changing climate. ",
        "/eu-adaptation-policy/sector-policies/land-use-planning",
    ),
    (
        "Marine and fisheries",
        "Climate change is expected to have severe impacts on the marine environment. Increase in "
        "water temperatures will contribute to a restructuring of marine ecosystems with implications "
        "for ocean circulation, biogeochemical cycling and marine biodiversity. Ocean acidification "
        "will affect the ability of some calcium carbonate-secreting species (as molluscs, planktons "
        "and corals) to produce their shells or skeletons. Warmer and more acidic seawater will "
        "therefore negatively affect fishery and aquaculture.",
        "/eu-adaptation-policy/sector-policies/marine-and-fisheries",
    ),
    (
        "Mountain areas",
        "By the end of the century, it is projected that European mountains will have changed physically. "
        "Glaciers will have experienced significant mass loss, but changes also impact the lower, mid-hills, "
        "and floodplain environments, thereby affecting water availability, agricultural production, tourism, "
        "and health sectors. Seasonal snow lines will be found at higher elevations, and snow seasons will "
        "become shorter. Tree lines will move up and forest patterns will change in lower elevations.",
        "/eu-adaptation-policy/sector-policies/mountain-areas",
    ),
    (
        "Tourism",
        "Since weather and climate have a decisive influence on the travel season and the choice of holiday "
        "destinations, the tourism industry is highly dependent on them. There is also a strong connection "
        "between nature and tourism, as well as between cultural heritage and tourism. Depending on the "
        "location and the time of the year tourism can be positively or negatively impacted by climate change.",
        "/eu-adaptation-policy/sector-policies/tourism",
    ),
    (
        "Transport",
        "The need for adapting the transport system to the impact of climate change has been highlighted since "
        "the European Commission's Adaptation White Paper (COM (2009)148). Transport adaptation is addressed "
        "through a combination of European transport, climate change and research policies. The European Union "
        "promotes best practices, mainstreaming adaptation within its transport infrastructure development "
        "programmes, and provides guidance, e.g. by developing adequate standards for construction. Action is "
        "focused on transport infrastructure, and particularly on the Trans-European Transport Network (TEN-T).",
        "/eu-adaptation-policy/sector-policies/transport",
    ),
    (
        "Urban",
        "In Europe, nearly 73% of the population live in urban areas and this is projected to increase to over "
        "80% by 2050. Climate change is likely to influence almost all components of cities and towns - their "
        "environment, economy and society.  This raises new, complex challenges for urban planning and management. "
        "Climate change impacts on the hubs of Europe's economic activity, social life, culture and innovation "
        "have repercussions far beyond their municipal borders.",
        "/eu-adaptation-policy/sector-policies/urban",
    ),
    (
        "Water management",
        "Water resources are directly impacted by climate change, and the management of these resources affects "
        "the vulnerability of ecosystems, socio-economic activities and human health. Water management is also "
        "expected to play an increasingly central role in adaptation. Climate change is projected to lead to major"
        "changes in water availability across Europe with increasing water scarcity and droughts mainly in Southern"
        "Europe and increasing risk of floods throughout most of Europe.",
        "/eu-adaptation-policy/sector-policies/water-management",
    ),
]
