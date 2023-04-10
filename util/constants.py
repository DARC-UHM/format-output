"""
This file holds basic data that is not changed each time format_and_output.py is run.
"""

# DSCRTP accepted null vals
NULL_VAL_INT = -999
NULL_VAL_STRING = 'NA'

# Column nums for after the json object is array-ized
# THESE MUST BE UPDATED WHENEVER COLUMNS SHIFT (see column nums in 'headers' below)
SAMPLE_ID = 0
TRACKING_ID = 1
SCIENTIFIC_NAME = 4
COMBINED_NAME_ID = 23
ID_COMMENTS = 25
OBSERVATION_DATE = 42
OBSERVATION_TIME = 43
INDV_COUNT = 57
VERBATIM_SIZE = 61
MIN_SIZE = 62
MAX_SIZE = 63
ASSOCIATED_TAXA = 66
OCCURRENCE_COMMENTS = 67
HABITAT = 71
SUBSTRATE = 72
CMECS_GEO_FORM = 73
IMAGE_PATH = 78
HIGHLIGHT_IMAGE = 79
IDENTITY_REF = 88
UPON_IS_CREATURE = 89
VARS_CONCEPT_NAME = 90

# column headers for output file
HEADERS = [
    'SampleID',  # 0
    'TrackingID',  # 1
    'Citation',  # 2
    'Repository',  # 3
    'ScientificName',  # 4
    'VernacularNameCategory',  # 5
    'VernacularName',  # 6
    'TaxonRank',  # 7
    'AphiaID',  # 8
    'LifeScienceIdentifier',  # 9
    'Phylum',  # 10
    'Class',  # 11
    'Subclass',  # 12
    'Order',  # 13
    'Suborder',  # 14
    'Family',  # 15
    'Subfamily',  # 16
    'Genus',  # 17
    'Subgenus',  # 18
    'Species',  # 19
    'Subspecies',  # 20
    'ScientificNameAuthorship',  # 21
    'Morphospecies',  # 22
    'CombinedNameID',  # 23
    'Synonyms',  # 24
    'IdentificationComments',  # 25
    'IdentifiedBy',  # 26
    'IdentificationDate',  # 27
    'IdentificationQualifier',  # 28
    'IdentificationVerificationStatus',  # 29
    'Ocean',  # 30
    'LargeMarineEcosystem',  # 31
    'Country',  # 32
    'FishCouncilRegion',  # 33
    'Locality',  # 34
    'Latitude',  # 35
    'Longitude',  # 36
    'DepthInMeters',  # 37
    'DepthMethod',  # 38
    'MinimumDepthInMeters',  # 39
    'MaximumDepthInMeters',  # 40
    'LocationComments',  # 41
    'ObservationDate',  # 42
    'ObservationTime',  # 43
    'SurveyID',  # 44
    'Vessel',  # 45
    'PI',  # 46
    'PIAffiliation',  # 47
    'Purpose',  # 48
    'SurveyComments',  # 49
    'Station',  # 50
    'EventID',  # 51
    'SamplingEquipment',  # 52
    'VehicleName',  # 53
    'SampleAreaInSquareMeters',  # 54 hardcoded for now, keeping column in case of future update (at request of DARC)
    'footprintWKT',  # 55 same ^
    'footprintSRS',  # 56 same ^
    'IndividualCount',  # 57
    'CategoricalAbundance',  # 58
    'Density',  # 59
    'Cover',  # 60
    'VerbatimSize',  # 61
    'MinimumSize',  # 62
    'MaximumSize',  # 63
    'WeightInKg',  # 64
    'Condition',  # 65
    'AssociatedTaxa',  # 66
    'OccurrenceComments',  # 67
    'LocationAccuracy',  # 68
    'NavType',  # 69
    'OtherData',  # 70
    'Habitat',  # 71
    'Substrate',  # 72
    'CMECSGeoForm',  # 73
    'Temperature',  # 74
    'Salinity',  # 75
    'Oxygen',  # 76
    'RecordType',  # 77
    'ImageFilePath',  # 78
    'HighlightImageFilePath',  # 79
    'DataProvider',  # 80
    'DataContact',  # 81
    'Modified',  # 82
    'WebSite',  # 83
    'EntryDate',  #84
    'Reporter',  # 85
    'ReporterEmail',  # 86
    'ReporterComments',  # 87
    'IdentityReference',  # 88 - All columns here and below are for reference and are not output to the final .tsv
    'UponIsCreature',  # 89
    'VARSConceptName'  # 90
]

# Substrate code translations and grain size order
SUB_CONCEPTS = {
    'sed': 'sediment',
    'peb': 'pebble',
    'cob': 'cobble',
    'bou': 'boulder',
    'bed': 'bedrock',
    'man': 'man-made',
    'dead': 'dead',
    'dik': 'dike rock formation of',
    'c': 'cemented',
    'b': 'basalt',
    'l': 'limestone',
    'fl': 'fluted',
    'blk': 'block',
    'nodmn': 'manganese nodules',
    'orgcn': 'Cnidaria',
    'orgal': 'algal organism',
    'orgrho': 'Rhodophyta',
    'rov': 'remotely operated underwater vehicle',
    'ven': 'vent',
    'mn': 'with manganese crust',
    'pi': ['pillow lava formation of', 'from pillow lava'],
    'a': 'composed of algal carbonate',
    't': 'talus',
    'po': 'pocket',
    'hp': 'of hydrothermal precipitate',
    'led': 'ledge',
    'cre': 'crevice',
    'cha': 'channel',
    'cav': 'cavity',
    'cra': 'crack',
    'bu': 'burrow',
    'mo': 'mound',
    'ho': 'hollow',
    'tr': 'track',
    'sc': 'sediment-covered',
    'tu': 'tube formation of',
    'mu': 'mudstone',
    'm': 'mudstone',
    'du': 'dunes',
    'ri': 'rippled',
    'col': 'columnar',
    'cn': 'Cnidaria',
    'spo': 'Porifera',
    'org': 'organism',
    ' org': 'organism',
    'art': 'artificial reef',
    'cem': 'cement',
    'fib': 'fiber object',
    'met': 'metallic object',
    'tra': 'trash',
    'ord': 'ordnance',
    'made': 'object',
    'wre': 'wreck',
    'pla': 'plastic object',
    'tube': 'Animal-made tube'
}

# VARS shorthand for substrates
ROOTS = ['sed', 'nodmn', 'peb', 'cob', 'bou', 'blk', 'bed', 'orgcn', 'orgal',
         'orgrho', 'dead', 'man', 'rov', 'ven', 'org', 'tube']

# VARS substrates that don't have a shorthand
SAMES = ['organism', 'man-made trash', 'Animal-made tube', 'debris',
         'sediment', 'pebble', 'cobble', 'boulder', 'bedrock']

"""
Suffixes and prefixes are additional descriptors added to a root. For example, 'scbedmn' consists of a prefix ('sc'), 
a root ('bed'), and a suffix ('mn'). These will be added together and the final translation will be 
'sediment-covered bedrock with manganese crust'.
"""
SUFFIXES = ['mn', 'pi', 'a', 't', 'po', 'hp']
SUFFIXES_FORMS = ['led', 'cre', 'cha', 'cav', 'cra', 'bu', 'mo', 'ho', 'tr', 'du']
PREFIXES = ['dik', 'fl', 'sc', 'tu', 'mu', 'ri', 'col', 'c', 'b', 'l', 'm']
SUFFIXES_DEAD = ['cn', 'spo', ' org']
SUFFIXES_MAN = ['art', 'cem', 'fib', 'met', 'tra', 'ord', 'made', 'wre', 'pla']

ALL_AFFIXES = SUFFIXES + SUFFIXES_FORMS + PREFIXES + SUFFIXES_DEAD + SUFFIXES_MAN
ALL_AFFIXES.sort(key=len, reverse=True)
