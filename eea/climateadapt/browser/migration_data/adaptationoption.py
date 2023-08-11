# -*- coding: utf-8 -*-
""" Open .xlsx
    Copy relevant data to Google Sheets
    Download CSV
    Save the content as python var here
"""

ADAPTATION_OPTION_MIGRATION_DATA = """
Adaptation measures to increase climate resilience of airports,,,,,,X,X,,,,,,,,,,,,X,,X
Integration of climate change adaptation in drought and water conservation plans,,X,X,,,,,,,,,,X,X,,,,,,,
Adaptation of fire management plans,,X,X,,,,,,,,,,X,,,,X,,,,
Adaptation of flood management plans,,X,X,,,,,,,,,,X,X,,,,,,,
Adaptation of groundwater management,,,,,,,X,,X,,,,,,,,,X,,,X
Integration of climate change adaptation in coastal management plans,,X,X,,,,,,,,,,X,X,,,,,,,
Integration of climate change adaptation in land use planning,,X,X,,,,,,,,,,X,X,,,,,,,
Adaptation options for electricity transmission and distribution networks and infrastructure,,,,,,X,X,,,,,,,,,,,,X,,X
Adaptation options for hydropower plants,,,,,,X,X,,,,,,,,,,,,X,,X
Improved desing of dikes and levees,,,,,,X,,,,,,,,,,,,,X,,
Adaptive management of natural habitats,X,,,,,,,X,X,,,,X,,,,,X,,,
Afforestation and reforestation as adaptation opportunity,,X,,,,,,X,,,,,X,,,,,X,,,
Agro-forestry,,,,,,,,X,,,X,,,,X,,,X,,,
Awareness raising campaigns for stakeholders’ behavioural change,,,,,,,,,,X,X,,,,X,X,,,,,
Beach and shoreface nourishment,,,,,,,,X,,,,,,,,,,X,,,
Capacity building on climate change adaptation,,,,,,,,,,,X,,,,,X,X,,,,
Cliff stabilisation and strengthening,,,,,,X,,X,,,,,,,,,,X,X,,,,,,,,,,,,,,,,,,,,,,,
Climate proofed construction and design standards for road infrastructure,,,,,,X,X,,,,,,,,,,,,X,,X
Climate proofing of buildings against excessive heat,,,,,,,X,X,,,,,,,,,,X,,,X,,,,,,,,,,,,,,,,,,,,,
Consumer-side adaptation options in the energy sector – changes in individual behaviour,,,,,,,,,,X,X,,,,X,,X,,,,
Crises and disaster management systems and plans,,X,,,,,,,,X,,,X,X,,,,,,X,
Desalinisation,,,,,,,X,,,,,,,,,,,,,,X
Diversification of fisheries and aquaculture products and systems,X,,,,,,,,,,X,,X,,X,,,,,,
Dune construction and strengthening,,,,,,,,X,,,,,,,,,,X,,,
Economic incentives for behavioural change,,,,X,,,,,,,X,X,,,X,,,,,,
Enhancing operational safety in offshore and inshore operations,,,,,,X,,,,,X,,,,X,,,,X,,
Establishment and restoration of riparian buffers,,,,,,,,X,X,,,,,,,,,X,,,
Establishment of early warning systems,,,,,,,X,,,X,,,,,,,X,,,,X
Floating and amphibious housing,,,,,,X,X,,,,,,,,,,,,X,,X
Floating or elevated roads,,,,,,X,,,,,,,,,,,,,X,,
Urban green infrastructure planning and nature-based solutions,,,,,,,,X,,,,,,,,,,X,,,
"Groynes, breakwaters and artificial reefs",,,,,,X,,,,,,,,,,,,,X,,
Heat health action plans,,X,,,,,,,,X,,,X,,,,X,,,,
Improve the functional connectivity of ecological networks,X,,,,,,,X,X,,,,X,,,,,X,,,
Improved water retention capacity in the agricultural landscape,,X,,,,,,X,,,,,X,,,,,X,,,
Improvement of irrigation efficiency,,,,,,,X,,,X,,,,,,,,,,,X
Insurance as risk management tool,X,,,,X,,,,,,,X,,X,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Operation and construction measures for ensuring climate-resilient railway infrastructure,,,,,,X,X,,,,,,,,,,,,X,,X
Raising and advancing coastal land,,,,,,X,,,,,,,,,,,,,X,,
Reducing water consumption for cooling of thermal generation plants,,,,,,X,X,,,,,,,,,,,,X,,X
Rehabilitation and restoration of rivers and floodplains,,,,,,,,X,X,,,,,,,,,X,,,
Restoration and management of coastal wetlands,,,,,,,,,X,,,,,,,,,X,,,
Retreat from high-risk areas,,X,,X,,,,,,,,X,X,,,,,,,,
Risk-based zoning and siting for aquaculture,,X,,,,,,,,X,,,X,X,,,,,,,
Seawalls and jetties,,,,,,X,,,,,,,,,,,,,X,,
Storm surge gates / flood barriers,,,,,,X,,,,,,,,,,,,,X,,
Climate smart urban agriculture,,,,,,,,X,,,X,,,,X,,,X,,,
Use of adapted crops and varieties,,,,,,,X,X,,,,,,,,,,X,,,X
Use of remote sensing in climate change adaptation,,,,,,,X,,,X,,,,,,,X,,,,X
Water reuse,,,,,,,X,,,,X,,,,,,,,,X,X
Water restrictions and water rationing,X,,,,,,,,,,X,,X,,X,,,,,,
Water sensitive forest management,,,,,,,,X,X,,,,,,,,,X,,,
Water sensitive urban and building design,,,,,,,X,X,,,,,,,,,,X,X,,
Water uses to cope with heat waves in cities,,,,,,X,X,,,,,,,,,,,,X,,X
Weather derivatives as risk management tool,X,,,,X,,,,,,,X,,X,,,,,,,
Precision agriculture,,,,,,,X,,,X,,,,,,,X,,,,X
Early warning systems for vector-borne diseases,,,,,,,X,,,X,,,,,,,X,,,,X
"""

# The order is not the same in vocabulary and csv for IPCC
MAP_IPCC = {
    0: 7,
    1: 9,
    2: 8,
    3: 6,
    4: 4,
    5: 5,
    6: 2,
    7: 0,
    8: 3,
    9: 1,
}
