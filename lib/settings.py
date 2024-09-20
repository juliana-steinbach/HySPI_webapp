USER_DB = 'user-db'
EI = 'ei_3.9.1'
PI = 'only premise inventories'

API_KEY = '8dd1a5bd80ce401a8fee652c805092cc'

# Method
EF = 'EF v3.0 no LT'

climate = (EF, 'climate change no LT', 'global warming potential (GWP100) no LT')
m_resources = (EF, 'material resources: metals/minerals no LT',
               'abiotic depletion potential (ADP): elements (ultimate reserves) no LT')
land = (EF, 'land use no LT', 'soil quality index no LT')
water = (EF, 'water use no LT', 'user deprivation potential (deprivation-weighted water consumption) no LT')
acidification = (EF, 'acidification no LT', 'accumulated exceedance (AE) no LT')
marine_eutroph = (EF, 'eutrophication: marine no LT', 'fraction of nutrients reaching marine end compartment (N) no LT')
freshwater_eutroph = (
    EF, 'eutrophication: freshwater no LT', 'fraction of nutrients reaching freshwater end compartment (P) no LT')
terre_eutroph = (EF, 'eutrophication: terrestrial no LT', 'accumulated exceedance (AE) no LT')
radiation = (EF, 'ionising radiation: human health no LT', 'human exposure efficiency relative to u235 no LT')
non_renew = (EF, 'energy resources: non-renewable no LT', 'abiotic depletion potential (ADP): fossil fuels no LT')

# List of the impacts
IMPACTS = [climate, m_resources, land, water, acidification, marine_eutroph, freshwater_eutroph, terre_eutroph,
           radiation, non_renew]