"""
This script is used to get VARS records from the HURL database and reformat them into
Deep Sea Corals Research and Technology Program's submission format. Also performs
various QA/QC checks and verifies taxa with WORMS.
"""

import json
import csv
import os
import errno

from datetime import timezone
from util.functions import *
from concept.concept_handler import *

OUTPUT_FILE_NAME = ''
OUTPUT_FILE_PATH = ''
SEQUENCE_NAMES_PATH = ''


"""#####################################################################################################################
If you need to run this script multiple times (e.g. for testing or troubleshooting), you can hardcode names and file
paths here so you don't have to enter them in the CLI every time. If these are left blank, the script will prompt you 
to enter this information at runtime. If you don't want to use the hardcoded values, simply comment out this block of 
code. """

# the name of the output file without the .tsv extension, e.g. 'NA134'
OUTPUT_FILE_NAME = 'test'
# path where you want the output file to be saved, e.g. '/Volumes/maxarray2/varsadditional/AnnotationExtracts'
OUTPUT_FILE_PATH = '/Users/darc/Desktop'
# path to a csv of the sequence names, e.g. '/Users/darc/Documents/GitHub/Format-Output/reference/test_sequences.csv'
SEQUENCE_NAMES_PATH = '/Users/darc/Documents/Github/Format-Output/reference/test_sequences.csv'

"""##################################################################################################################"""


# Initialization: Get the cache directory (note: does not consider Linux file structure)
current_folder = os.getcwd()

if os.name == 'nt':
    # Windows
    save_folder = os.getenv('LOCALAPPDATA')
else:
    # Mac
    save_folder = os.getenv('HOME') + '/Library/Application Support'

os.chdir(save_folder)

try:
    os.mkdir('CTDProcess')
except OSError as err:
    if err.errno != errno.EEXIST:
        # if the OS error is something other than 'directory already exists', raise the error
        raise
    # otherwise, ignore the error
    pass

save_folder = os.path.join(save_folder, 'CTDProcess')
print(f'\nSaved cache files located in: {save_folder}')

os.chdir(current_folder)

dive_info = []  # the script's copy of Dives.csv

# Load info from Dives.csv: Dives.csv must be in the same directory that the script was called. This file must be
# up to date with all video sequences listed in the input file
with open('reference/Dives.csv', 'r', encoding='utf-8') as dive_csv:
    reader = csv.reader(dive_csv)
    dive_info_headers = next(reader)
    for row in reader:
        dive_info.append(row)

# Decides whether to load or overwrite concepts
load_concepts = input('\nShould the program load previously encountered concept names '
                      'from saved file for a faster runtime?\n\n'
                      'Y: Use the file \n'
                      'N: Use WoRMS and overwrite the file (takes 15-20 minutes) \n\n'
                      '>> ').lower() in ['y', 'yes']

concepts = {}

if load_concepts:
    try:
        os.chdir(save_folder)
        with open('concepts.json') as file:
            concepts = json.load(file)
    except FileNotFoundError:
        print('No concepts file found; using WoRMS instead')

output_file_name = OUTPUT_FILE_NAME or input('Name of output file (without the .tsv file extension: ')
output_file_path = OUTPUT_FILE_PATH or input('Path to folder of output files: ')
sequence_names_path = SEQUENCE_NAMES_PATH or input("Path to a list of sequence names: ")

sequence_names = []  # list of video sequences numbers to query VARS API

with open(sequence_names_path, 'r') as seq_names_file:
    seq_reader = csv.reader(seq_names_file)
    h = next(seq_reader)
    for row in seq_reader:
        sequence_names.append(row[1])

# GeoForm: declaring here so val is saved across multiple annotations AND multiple dives
# (this is only updated once per major change in VARS)
current_cmecs_geo_form = NULL_VAL_STRING

full_report_records = []  # list of every concept formatted for final output
observation_messages = [OBSERVATION_HEADERS]  # list of items to review (QA/QC)

if load_concepts:
    print("\n%-35s%-30s%-30s%-s" % ('Dive Name', 'Annotations Found', 'Duplicates Removed', 'Status'))
    print('=========================================================================================================')

# Iterates over each dive listed in the input CSV file
for dive_name in sequence_names:
    first_round = True  # to print header in terminal
    report_records = []  # array of concepts records for the dive
    concepts_from_save = 0  # count of how many concepts were loaded from the saved concepts file
    concepts_from_worms = 0   # count of how many concepts were loaded from worms

    if load_concepts:
        print('%-35s' % dive_name, end='')
        sys.stdout.flush()
    else:
        print(f'\nFetching annotations for {dive_name}')

    url = f'http://hurlstor.soest.hawaii.edu:8086/query/dive/{dive_name.replace(" ", "%20")}'

    with requests.get(url) as r:
        report_json = r.json()

    # Tries to get the current dive from Dives.csv, links information from Dives.csv to the current dive
    dive_row = next((row for row in dive_info if row[0] in dive_name or dive_name in row[0]), None)
    if not dive_row:
        print('\n###################################################################')
        print(f'ERROR: Dive "{dive_name}" not found in Dives.csv file.')
        print('This dive must be added to Dives.csv to continue processing.')
        print('###################################################################\n')
        break

    for i in range(len(dive_row)):
        if dive_row[i] == '':
            dive_row[i] = NULL_VAL_STRING
    dive_dict = dict(zip(dive_info_headers, dive_row))

    if load_concepts:
        print('%-30s' % len(report_json['annotations']), end='')
        sys.stdout.flush()
    else:
        print(f'{len(report_json["annotations"])} annotations found')

    # sort objects by uuid - this is so the final output can match the expected output for easier testing
    report_json['annotations'].sort(key=extract_uuid)
    # Sort json objects by time
    report_json['annotations'].sort(key=extract_time)

    if dive_dict['LocationAccuracy'] == NULL_VAL_STRING:
        observation_messages.append([
            dive_name,
            NULL_VAL_STRING,
            NULL_VAL_STRING,
            NULL_VAL_STRING,
            'LocationAccuracy',
            NULL_VAL_STRING,
            2,
            'No location accuracy for this dive. Add this information to the dive record in Dives.csv'
        ])

    if dive_dict['WebSite'] == NULL_VAL_STRING:
        observation_messages.append([
            dive_name,
            NULL_VAL_STRING,
            NULL_VAL_STRING,
            NULL_VAL_STRING,
            'WebSite',
            NULL_VAL_STRING,
            2,
            'No website found for this dive. Add this information to the dive record in Dives.csv'
        ])

    # get start time and end time of each video (to use later to check whether annotation falls inside a video time)
    dive_video_timestamps = []
    for i in range(len(report_json['media'])):
        media = report_json['media'][i]
        # the second check here can be removed if we need to consider clips longer than 10 minutes
        #                                     ↓           remove me               ↓
        if 'image' not in media['video_name'] and media['duration_millis'] > 600000:  # 600000 millis = 10 mins
            start_time = parse_datetime(report_json['media'][i]['start_timestamp'])
            dive_video_timestamps.append([start_time, start_time + timedelta(milliseconds=media['duration_millis'])])

    # Loops through all annotations and fills out the fields required by DSCRTP
    for annotation in report_json['annotations']:
        record_dict = dict(zip(HEADERS, [NULL_VAL_STRING] * len(HEADERS)))

        concept_name = annotation['concept']
        recorded_time = parse_datetime(annotation['recorded_timestamp'])
        if recorded_time.microsecond >= 500000:
            recorded_time = recorded_time + timedelta(seconds=1)
        formatted_timestamp = '{:02}:{:02}:{:02}'.format(recorded_time.hour, recorded_time.minute, recorded_time.second)

        record_dict['VARSConceptName'] = concept_name
        record_dict['SampleID'] = dive_name.replace(' ', '_') + '_' + formatted_timestamp
        record_dict['TrackingID'] = annotation['observation_uuid']
        record_dict['Repository'] = (dive_dict['DataProvider'].split(';')[0]
                                     + ' | University of Hawaii Deep-sea Animal Research Center')

        aphia_id = NULL_VAL_INT
        tax_rank = NULL_VAL_STRING
        scientific_name = NULL_VAL_STRING
        authorship = NULL_VAL_STRING
        synonyms = NULL_VAL_STRING
        descriptors = []
        taxon_ranks = {}
        vernacular_name = NULL_VAL_STRING

        if concept_name != 'none':
            # If concept name not in save concepts file, searches WoRMS
            if concept_name not in concepts:
                if first_round:
                    first_round = False
                    print('\n\nWoRMS check:')
                    print("\n%-40s %-35s%-15s%-15s%-15s%-15s" %
                          ('VARS Concept Name', 'WoRMS Query', 'Taxon Record', 'Taxon Tree', 'Vernaculars',
                           'Synonyms (VARS)'))
                    print('============================================================================================'
                          '============================================')
                concept = Concept(concept_name)
                cons_handler = ConceptHandler(concept)
                cons_handler.fetch_worms_aphia_record()
                cons_handler.fetch_worms_taxon_tree()
                cons_handler.fetch_vernaculars()
                cons_handler.fetch_vars_synonyms()
                concepts[concept_name] = {
                    'scientific_name': concept.scientific_name,
                    'aphia_id': concept.aphia_id,
                    'authorship': concept.authorship,
                    'synonyms': concept.synonyms,
                    'taxon_rank': concept.taxon_rank,
                    'taxon_ranks': concept.taxon_ranks,
                    'descriptors': concept.descriptors,
                    'vernacular_name': concept.vernacular_names
                }
                if concept.cf_flag:
                    observation_messages.append([
                        dive_name,
                        annotation['observation_uuid'],
                        annotation['concept'],
                        recorded_time,
                        'Concept name',
                        concept_name,
                        0,
                        'Concept name contains cf; requires manual review for placement.'
                    ])
                if concept.concept_name_flag:
                    observation_messages.append([
                        dive_name,
                        annotation['observation_uuid'],
                        annotation['concept'],
                        recorded_time,
                        'Concept name',
                        concept_name,
                        2,
                        'No words in concept match any object in WoRMS database. Check for spelling errors and fix.'
                    ])
                concepts_from_worms += 1
            else:
                concepts_from_save += 1

            scientific_name = concepts[concept_name]['scientific_name']
            aphia_id = concepts[concept_name]['aphia_id']
            authorship = concepts[concept_name]['authorship']
            synonyms = ' | '.join(concepts[concept_name]['synonyms']) if concepts[concept_name]['synonyms'] \
                else NULL_VAL_STRING
            tax_rank = concepts[concept_name]['taxon_rank']
            taxon_ranks = concepts[concept_name]['taxon_ranks']
            descriptors = concepts[concept_name]['descriptors']
            vernacular_name = concepts[concept_name]['vernacular_name']

            # Fill out the taxonomy from the taxon ranks
            if taxon_ranks != {}:
                for key in ['Kingdom', 'Phylum', 'Class', 'Subclass', 'Order',
                            'Suborder', 'Family', 'Subfamily', 'Genus',
                            'Subgenus', 'Species', 'Subspecies']:
                    if key in taxon_ranks:
                        record_dict[key] = taxon_ranks[key]

        # checking this first because we use this field to populate other fields :)
        media_type = 'still image'
        # loop through timestamps and check if recorded_timestamps is in timestamps
        for i in range(len(dive_video_timestamps)):
            if dive_video_timestamps[i][0] <= recorded_time <= dive_video_timestamps[i][1]:
                media_type = 'video observation'
                break
        record_dict['RecordType'] = media_type

        if scientific_name != NULL_VAL_STRING:  # this row is also 'out of order' but must be filled before id comments
            record_dict['IdentificationQualifier'] = \
                'ID by expert from video' if media_type == 'video observation' else 'ID by expert from image'

        record_dict['Citation'] = dive_dict['Citation'] if dive_dict['Citation'] != NULL_VAL_STRING else ''
        record_dict['ScientificName'] = scientific_name
        record_dict['VerbatimScientificName'] = scientific_name
        record_dict['VernacularName'] = vernacular_name
        record_dict['TaxonRank'] = tax_rank
        record_dict['AphiaID'] = aphia_id
        if aphia_id != NULL_VAL_INT:
            record_dict['LifeScienceIdentifier'] = f'urn:lsid:marinespecies.org:taxname:{aphia_id}'
        record_dict['ScientificNameAuthorship'] = authorship
        record_dict['CombinedNameID'] = scientific_name
        if descriptors:
            record_dict['Morphospecies'] = ' '.join(descriptors)
            # we don't want a combined name id of 'NA [descriptors]', just '[descriptors]'
            if record_dict['CombinedNameID'] != NULL_VAL_STRING:
                record_dict['CombinedNameID'] += f' {record_dict["Morphospecies"]}'
            else:
                record_dict['CombinedNameID'] = record_dict['Morphospecies']
        record_dict['Synonyms'] = synonyms
        id_comments = get_association(annotation, 'identity-certainty')
        if id_comments:
            id_comments = id_comments['link_value']
            id_comments = id_comments.split('; ')
            if 'maybe' in id_comments:
                record_dict['IdentificationQualifier'] = record_dict['IdentificationQualifier'] + ' | ID Uncertain'
                id_comments.remove('maybe')
            id_comments = ' | '.join(id_comments)
            record_dict['IdentificationComments'] = id_comments if id_comments != '' else NULL_VAL_STRING
        record_dict['IdentifiedBy'] = convert_username_to_name(annotation['observer'])
        observation_time = parse_datetime(annotation['observation_timestamp'])
        record_dict['IdentificationDate'] = observation_time.strftime('%Y-%m-%d')
        record_dict['IdentificationVerificationStatus'] = 1
        record_dict['Ocean'] = dive_dict['Ocean']
        record_dict['LargeMarineEcosystem'] = dive_dict['LargeMarineEcosystem']
        record_dict['Country'] = dive_dict['Country']
        record_dict['FishCouncilRegion'] = dive_dict['FishCouncilRegion']
        record_dict['Locality'] = dive_dict['Locality'].replace(',', ' |')
        record_dict['Latitude'] = round(annotation['ancillary_data']['latitude'], 8)
        record_dict['Longitude'] = round(annotation['ancillary_data']['longitude'], 8)
        if 'depth_meters' in annotation['ancillary_data']:
            record_dict['DepthInMeters'] = round(annotation['ancillary_data']['depth_meters'], 3)
        else:
            record_dict['DepthInMeters'] = NULL_VAL_INT
            observation_messages.append([
                dive_name,
                annotation['observation_uuid'],
                annotation['concept'],
                recorded_time,
                'Depth in meters',
                '',
                1,
                'No depth measurement included in this record.'
            ])
        record_dict['MinimumDepthInMeters'] = record_dict['DepthInMeters']
        record_dict['MaximumDepthInMeters'] = record_dict['DepthInMeters']
        record_dict['DepthMethod'] = 'reported'
        record_dict['ObservationDate'] = recorded_time.strftime('%Y-%m-%d')
        record_dict['ObservationTime'] = recorded_time.strftime('%H:%M:%S')
        record_dict['SurveyID'] = dive_dict['SurveyID']
        record_dict['Vessel'] = dive_dict['Vessel']
        record_dict['PI'] = dive_dict['PI']
        record_dict['PIAffiliation'] = dive_dict['PIAffiliation']
        record_dict['Purpose'] = dive_dict['Purpose']
        record_dict['Station'] = dive_dict['Station']
        record_dict['EventID'] = dive_dict['EventID']
        record_dict['SamplingEquipment'] = dive_dict['SamplingEquipment']
        record_dict['VehicleName'] = dive_dict['VehicleName']
        # hardcoded for now, keeping column in case of future update
        record_dict['SampleAreaInSquareMeters'] = NULL_VAL_INT
        pop_quantity = get_association(annotation, 'population-quantity')
        if pop_quantity:
            record_dict['IndividualCount'] = pop_quantity['link_value']
        elif record_dict['ScientificName'] != NULL_VAL_STRING:
            record_dict['IndividualCount'] = '1'
        else:
            record_dict['IndividualCount'] = NULL_VAL_INT
        cat_abundance = get_association(annotation, 'categorical-abundance')
        if cat_abundance:
            record_dict['CategoricalAbundance'] = cat_abundance['link_value']
            record_dict['IndividualCount'] = NULL_VAL_INT
        record_dict['Density'] = NULL_VAL_INT  # hardcoded for now, keeping column in case of future update
        record_dict['Cover'] = NULL_VAL_INT  # hardcoded for now, keeping column in case of future update
        min_size = NULL_VAL_INT
        max_size = NULL_VAL_INT
        size_str = NULL_VAL_STRING
        size_category = get_association(annotation, 'size')
        if size_category:
            size_str = size_category['to_concept']
            # turns a 'size category' into a maximum and minimum size
            match size_str:
                case '0-10 cm':
                    min_size = '0'
                    max_size = '10'
                case '10-30 cm':
                    min_size = '10'
                    max_size = '30'
                case '30-50 cm':
                    min_size = '30'
                    max_size = '50'
                case '50-100 cm':
                    min_size = '50'
                    max_size = '100'
                case 'greater than 100 cm':
                    min_size = '101'
                case _:
                    # flag warning
                    observation_messages.append([
                        dive_name,
                        annotation['observation_uuid'],
                        annotation['concept'],
                        recorded_time,
                        'Size',
                        size_str,
                        1,
                        'String not recognized as an established size category.'
                    ])
        record_dict['VerbatimSize'] = size_str
        record_dict['MinimumSize'] = min_size
        record_dict['MaximumSize'] = max_size
        record_dict['WeightInKg'] = NULL_VAL_INT  # hardcoded for now, keeping column in case of future update
        condition_comment = get_association(annotation, 'condition-comment')
        if condition_comment:
            if condition_comment['link_value'] in ['dead', 'Dead']:
                # flag warning
                observation_messages.append([
                    dive_name,
                    annotation['observation_uuid'],
                    annotation['concept'],
                    recorded_time,
                    'Condition comment',
                    condition_comment,
                    1,
                    'Dead creatures should typically not be reported.'
                ])
                record_dict['Condition'] = 'Dead'
            else:
                record_dict['Condition'] = 'Damaged'
        else:
            record_dict['Condition'] = 'Live' if record_dict['ScientificName'] != NULL_VAL_STRING else NULL_VAL_STRING

        # build occurrence remark string
        occurrence_remark = get_associations_list(annotation, 'occurrence-remark')
        remark_string = NULL_VAL_STRING
        if occurrence_remark:
            remark_list = []
            remark_string = ''
            for remark in occurrence_remark:
                remark_list.append(remark['link_value'])
            remark_string = ' | '.join(remark_list)
        if size_str != NULL_VAL_STRING:
            if remark_string != NULL_VAL_STRING:
                remark_string += ' | size is estimated greatest length of individual in cm. Size estimations placed into size category bins'
            else:
                remark_string = 'size is estimated greatest length of individual in cm. Size estimations placed into size category bins'
        sampled_by = get_association(annotation, 'sampled-by')
        if sampled_by:
            if remark_string != NULL_VAL_STRING:
                remark_string += f' | sampled by {sampled_by["to_concept"]}'
            else:
                remark_string = f'sampled by {sampled_by["to_concept"]}'
        sample_ref = get_association(annotation, 'sample-reference')
        if sample_ref:
            record_dict['TrackingID'] += f' | {sample_ref["link_value"]}'

        record_dict['OccurrenceComments'] = remark_string
        record_dict['VerbatimLatitude'] = annotation['ancillary_data']['latitude']
        record_dict['VerbatimLongitude'] = annotation['ancillary_data']['longitude']
        record_dict['LocationAccuracy'] = \
            add_meters(dive_dict['LocationAccuracy']) if dive_dict['LocationAccuracy'] != 'NA' else ''
        record_dict['NavType'] = \
            'USBL' if dive_dict['Vessel'] == 'Okeanos Explorer' or dive_dict['Vessel'] == 'Nautilus' else 'NA'
        record_dict['OtherData'] = 'CTD'

        record_dict['WebSite'] = dive_dict['WebSite']

        # if there is a cmecs geo form, update
        if get_association(annotation, 'habitat'):
            current_cmecs_geo_form = f'{get_association(annotation, "megahabitat")["to_concept"]}, ' \
                                     f'{get_association(annotation, "habitat")["to_concept"]}'
        record_dict['CMECSGeoForm'] = current_cmecs_geo_form

        # habitat stuff
        primary = ''
        secondary = []
        s1 = get_association(annotation, 's1')
        if s1:
            primary = translate_substrate_code(s1['to_concept'])
            if not primary:
                # flag warning
                observation_messages.append([
                    dive_name,
                    annotation['observation_uuid'],
                    annotation['concept'],
                    recorded_time,
                    's1',
                    s1['to_concept'],
                    1,
                    f'Missing s1 or could not parse substrate code {s1["to_concept"]}.'
                ])
            else:
                record_dict['Habitat'] = f'primarily: {primary}'

        s2_records = get_associations_list(annotation, 's2')
        if len(s2_records) != 0:
            s2s_list = []
            for s2 in s2_records:  # remove duplicates
                if s2['to_concept'] not in s2s_list:
                    s2s_list.append(s2['to_concept'])
            s2s_list.sort(key=grain_size)
            for s2 in s2s_list:
                s2_temp = translate_substrate_code(s2)
                if s2_temp:
                    secondary.append(s2_temp)
            if len(secondary) != len(s2s_list):
                observation_messages.append([
                    dive_name,
                    annotation['observation_uuid'],
                    annotation['concept'],
                    recorded_time,
                    's2',
                    '; '.join(s2s_list),
                    1,
                    f'Could not parse a substrate code from list {secondary}.'
                ])
            record_dict['Habitat'] = record_dict['Habitat'] + f' / secondary: {"; ".join(secondary)}'
        habitat_comment = get_association(annotation, 'habitat-comment')
        if habitat_comment:
            record_dict['Habitat'] = record_dict['Habitat'] + f' / comments: {habitat_comment["link_value"]}'

        # checks if the item reported in 'upon' is in the list of accepted substrates - see translate_substrate_code
        # (substrate = ground, basically)
        upon = get_association(annotation, 'upon')
        record_dict['UponIsCreature'] = False
        if upon:
            subs = translate_substrate_code(upon['to_concept'])
            if subs:
                record_dict['Substrate'] = subs
            else:
                # if the item in 'upon' is not in the substrate list, it must be upon another creature
                record_dict['Substrate'] = upon['to_concept']
                record_dict['UponIsCreature'] = True

        identity_reference = get_association(annotation, 'identity-reference')
        if identity_reference:
            record_dict['IdentityReference'] = int(identity_reference['link_value'])
        else:
            record_dict['IdentityReference'] = -1
        if 'temperature_celsius' in annotation['ancillary_data']:
            record_dict['Temperature'] = round(annotation['ancillary_data']['temperature_celsius'], 4)
        else:
            record_dict['Temperature'] = NULL_VAL_INT
            # flag warning
            observation_messages.append([
                dive_name,
                annotation['observation_uuid'],
                annotation['concept'],
                recorded_time,
                'Temperature',
                '',
                1,
                'No temperature measurement included in this record.'
            ])
        if 'salinity' in annotation['ancillary_data']:
            record_dict['Salinity'] = round(annotation['ancillary_data']['salinity'], 4)
        else:
            record_dict['Salinity'] = NULL_VAL_INT
            # flag warning
            observation_messages.append([
                dive_name,
                annotation['observation_uuid'],
                annotation['concept'],
                recorded_time,
                'Salinity',
                '',
                1,
                'No salinity measurement included in this record.'
            ])
        if 'oxygen_ml_l' in annotation['ancillary_data']:
            # convert to mL/L
            record_dict['Oxygen'] = round(annotation['ancillary_data']['oxygen_ml_l'] / 1.42903, 4)
        else:
            record_dict['Oxygen'] = NULL_VAL_INT
            # flag warning
            observation_messages.append([
                dive_name,
                annotation['observation_uuid'],
                annotation['concept'],
                recorded_time,
                'Oxygen',
                '',
                1,
                'No oxygen measurement included in this record.'
            ])

        images = annotation['image_references']
        image_paths = []
        for image in images:
            image_paths.append(image['url'].replace(
                'http://hurlstor.soest.hawaii.edu/imagearchive',
                'https://hurlimage.soest.hawaii.edu'))

        if len(image_paths) == 1:
            record_dict['ImageFilePath'] = image_paths[0]
        elif len(image_paths) > 1:
            if '.png' in image_paths[0]:
                record_dict['ImageFilePath'] = image_paths[0]
            else:
                record_dict['ImageFilePath'] = image_paths[1]

        highlight_image = get_association(annotation, 'guide-photo')
        if highlight_image and highlight_image['to_concept'] == '1 best':
            record_dict['HighlightImageFilePath'] = record_dict['ImageFilePath']

        record_dict['DataProvider'] = dive_dict['DataProvider']
        record_dict['DataContact'] = dive_dict['DataContact']
        record_dict['Modified'] = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        record_dict['Reporter'] = 'Bingo, Sarah'
        record_dict['ReporterEmail'] = 'sarahr6@hawaii.edu'
        record_dict['EntryDate'] = ''  # this is left blank, to be filled by DSCRTP admin
        record = [record_dict[x] for x in HEADERS]
        report_records.append(record)

    identity_references = {}
    dupes_removed = 0

    # Collapse records with the same identity-reference
    num_records = len(report_records)
    i = 0
    while i < num_records:
        id_ref = report_records[i][IDENTITY_REF]
        if id_ref != -1:
            if id_ref not in identity_references:
                identity_references[id_ref] = report_records[i]
            else:
                for j in [ID_COMMENTS, HABITAT, SUBSTRATE, INDV_COUNT, VERBATIM_SIZE, OCCURRENCE_COMMENTS, CMECS_GEO_FORM]:
                    if identity_references[id_ref][j] == NULL_VAL_STRING and report_records[i][j] != NULL_VAL_STRING:
                        identity_references[id_ref][j] = report_records[i][j]
                for j in [MIN_SIZE, MAX_SIZE]:
                    if identity_references[id_ref][j] == NULL_VAL_INT and report_records[i][j] != NULL_VAL_INT:
                        identity_references[id_ref][j] = report_records[i][j]
                for j in [IMAGE_PATH, HIGHLIGHT_IMAGE]:
                    if report_records[i][j] != NULL_VAL_STRING:
                        if identity_references[id_ref][j] != NULL_VAL_STRING and \
                                report_records[i][j] not in identity_references[id_ref][j]:
                            identity_references[id_ref][j] += f' | {report_records[i][j]}'
                        else:
                            identity_references[id_ref][j] = report_records[i][j]
                if int(identity_references[id_ref][INDV_COUNT]) < int(report_records[i][INDV_COUNT]):
                    identity_references[id_ref][INDV_COUNT] = report_records[i][INDV_COUNT]
                del report_records[i]
                i -= 1
                num_records -= 1
                dupes_removed += 1
        i += 1

    if load_concepts:
        print('%-30s' % str(dupes_removed), end='')
        sys.stdout.flush()
    else:
        print(f'\n{str(dupes_removed)} duplicate records removed')

    # Fills in the AssociatedTaxa fields: retrieves records from the output table that have another VARS concept listed
    # as a substrate.
    for i in range(len(report_records)):
        associate_record = report_records[i]
        if associate_record[UPON_IS_CREATURE]:  # if the associate's 'upon' is indeed a creature
            host_concept_name = associate_record[SUBSTRATE]  # VARS name for host
            if host_concept_name in concepts:  # checks if host concept is in local concepts file
                # the timestamp at which the associate was recorded
                observation_time = get_date_and_time(associate_record)
                found = False
                for j in range(i + 10, -1, -1):
                    ''' checks backward, looking for the most recent host w/ matching name. we start at i + 10 because 
                        there can be multiple records with the exact same timestamp, and one of those records could be 
                        the 'upon' '''
                    # to catch index out of range exception
                    while j >= len(report_records):
                        j -= 1
                    host_record = report_records[j]

                    if i == j or j > i and get_date_and_time(host_record) != observation_time:
                        # i == j: record shouldn't be associated with itself, ignore
                        # other bit: host record won't be recorded after associate record, so ignore this record
                        pass
                    elif host_record[SAMPLE_ID][:-9] != associate_record[SAMPLE_ID][:-9]:
                        # dive names don't match, stop the search
                        break
                    else:
                        if host_record[VARS_CONCEPT_NAME] == host_concept_name:
                            # the host record's name is equal to the host concept name (associate's 'upon' name)
                            upon_time = get_date_and_time(host_record)
                            # if the host's 'associated taxa' field is blank, add the associate's concept name
                            if host_record[ASSOCIATED_TAXA] == NULL_VAL_STRING:
                                host_record[ASSOCIATED_TAXA] = associate_record[COMBINED_NAME_ID]
                            # otherwise, append the concept name if it's not already there
                            elif associate_record[COMBINED_NAME_ID] not in host_record[ASSOCIATED_TAXA]:
                                host_record[ASSOCIATED_TAXA] += f' | {associate_record[COMBINED_NAME_ID]}'
                            # add touch to occurrence comments
                            if host_record[OCCURRENCE_COMMENTS] == NULL_VAL_STRING:
                                host_record[OCCURRENCE_COMMENTS] = 'associate touching host'
                            elif 'associate touching host' not in host_record[OCCURRENCE_COMMENTS]:
                                host_record[OCCURRENCE_COMMENTS] += ' | associate touching host'
                            time_diff = observation_time - upon_time
                            if time_diff.seconds > 300:
                                # flag warning
                                observation_messages.append([
                                    dive_name,
                                    associate_record[TRACKING_ID],
                                    associate_record[SCIENTIFIC_NAME],
                                    observation_time,
                                    'Associated taxa',
                                    host_concept_name,
                                    1,
                                    f'Time between record and upon record greater than 5 minutes ({time_diff.seconds} seconds).'
                                ])
                            elif time_diff.seconds > 60:
                                # flag for review
                                observation_messages.append([
                                    dive_name,
                                    associate_record[TRACKING_ID],
                                    associate_record[SCIENTIFIC_NAME],
                                    observation_time,
                                    'Associated taxa',
                                    host_concept_name,
                                    0,
                                    f'Time between record and upon record greater than 1 minute ({time_diff.seconds} seconds).'
                                ])
                            found = True
                            break
                if not found:
                    # flag error
                    observation_messages.append([
                        dive_name,
                        associate_record[TRACKING_ID],
                        associate_record[SCIENTIFIC_NAME],
                        observation_time,
                        'Associated taxa',
                        host_concept_name,
                        2,
                        'Upon of specified concept name not found in previous records. Make sure this creature is annotated.'
                    ])
            else:
                # flag error
                observation_messages.append([
                    dive_name,
                    associate_record[TRACKING_ID],
                    associate_record[SCIENTIFIC_NAME],
                    get_date_and_time(associate_record),
                    'Associated taxa',
                    associate_record[SUBSTRATE],
                    2,
                    f'\"{associate_record[SUBSTRATE]}\" is listed as the host for this record, but that concept name '
                    'was not found in concepts. Double-check spelling of concept name.'
                ])

    # translate substrate (upon) names - this must be done after finding the associated taxa (relies on concept name)
    for i in range(len(report_records)):
        record = report_records[i]
        if record[SUBSTRATE] == 'organism (dead)':
            record[SUBSTRATE] = 'dead organism'
        elif record[SUBSTRATE] in concepts:
            saved = concepts[record[SUBSTRATE]]
            record[SUBSTRATE] = saved["scientific_name"]
            if saved["descriptors"]:
                record[SUBSTRATE] += f' ({" ".join(saved["descriptors"])})'

    # Add this formatted dive to the full list of report associate_records
    full_report_records += report_records
    print('Complete')

# Save everything into output files
print('\nSaving output files...')
os.chdir(save_folder)
with open('concepts.json', 'w') as file:
    json.dump(concepts, file)
os.chdir(output_file_path)
with open(output_file_name + '.tsv', 'w', newline='', encoding='utf-8') as file:
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(HEADERS[:88])
    for record in full_report_records:
        csv_writer.writerow(record[:88])
with open(output_file_name + '_messages.tsv', 'w', newline='', encoding='utf-8') as file:
    csv_writer = csv.writer(file, delimiter='\t')
    for message in observation_messages:
        csv_writer.writerow(message)
print(f'Output files saved at {output_file_path}')
print(f'There are {str(len(observation_messages) - 1)} messages to review.')
