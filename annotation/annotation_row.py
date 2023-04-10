from datetime import datetime, timezone
from typing import Dict

from annotation.timestamp_processor import TimestampProcessor
from util.constants import NULL_VAL_STRING, HEADERS, NULL_VAL_INT
from util.functions import get_association, convert_username_to_name, get_associations_list, add_meters, \
    translate_substrate_code, grain_size
from util.terminal_output import Color


# Reporter values - update these if reporter changes
REPORTER = 'Bingo, Sarah'
REPORTER_EMAIL = 'sarahr6@hawaii.edu'


# todo add tests
class AnnotationRow:
    """ Stores information for a specific annotation. See util.constants.HEADERS for a list of all the columns. """

    def __init__(self, annotation: Dict):
        """
        :param dict annotation: A VARS annotation object retrieved from the HURL server.
        """
        self.columns = dict(zip(HEADERS, [NULL_VAL_STRING] * len(HEADERS)))  # inits dict of header keys with NA vals
        self.annotation = annotation
        self.recorded_time = TimestampProcessor(self.annotation['recorded_timestamp'])
        self.observation_time = TimestampProcessor(self.annotation['observation_timestamp'])

    def set_simple_static_data(self):
        """
        Sets simple annotation data directly from the annotation JSON object.
        """
        self.columns['VARSConceptName'] = self.annotation['concept']
        self.columns['TrackingID'] = self.annotation['observation_uuid']
        self.columns['AphiaID'] = NULL_VAL_INT
        self.columns['IdentifiedBy'] = convert_username_to_name(self.annotation['observer'])
        self.columns['IdentificationDate'] = self.observation_time.timestamp.strftime('%Y-%m-%d')
        self.columns['IdentificationVerificationStatus'] = 1
        self.columns['Latitude'] = round(self.annotation['ancillary_data']['latitude'], 8)
        self.columns['Longitude'] = round(self.annotation['ancillary_data']['longitude'], 8)
        self.columns['DepthInMeters'] = round(self.annotation['ancillary_data']['depth_meters'], 3) \
            if 'depth_meters' in self.annotation['ancillary_data'] else NULL_VAL_INT
        self.columns['MinimumDepthInMeters'] = self.columns['DepthInMeters']
        self.columns['MaximumDepthInMeters'] = self.columns['DepthInMeters']
        self.columns['DepthMethod'] = 'reported'
        self.columns['ObservationDate'] = self.recorded_time.timestamp.strftime('%Y-%m-%d')
        self.columns['ObservationTime'] = self.recorded_time.timestamp.strftime('%H:%M:%S')
        self.columns['VerbatimLatitude'] = self.annotation['ancillary_data']['latitude']
        self.columns['VerbatimLongitude'] = self.annotation['ancillary_data']['longitude']
        self.columns['OtherData'] = 'CTD'
        self.columns['Modified'] = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        self.columns['Reporter'] = REPORTER  # defined at top of file
        self.columns['ReporterEmail'] = REPORTER_EMAIL  # ""

        self.columns['EntryDate'] = ''  # this column is left blank, to be filled by DSCRTP admin

        # these eight values are hardcoded for now, keeping columns in case of future update
        self.columns['SampleAreaInSquareMeters'] = NULL_VAL_INT
        self.columns['Density'] = NULL_VAL_INT
        self.columns['Cover'] = NULL_VAL_INT
        self.columns['WeightInKg'] = NULL_VAL_INT
        self.columns['SampleAreaInSquareMeters'] = NULL_VAL_INT
        self.columns['Density'] = NULL_VAL_INT
        self.columns['Cover'] = NULL_VAL_INT
        self.columns['WeightInKg'] = NULL_VAL_INT

    def set_sample_id(self, dive_name: str):
        """
        Sets the SampleID column with the properly formatted SampleID: [DIVE_NAME]_[TIMESTAMP]

        :param str dive_name: The name of the dive, e.g. 'Deep Discoverer 14040201'
        """
        self.columns['SampleID'] = dive_name.replace(' ',
                                                     '_') + '_' + self.recorded_time.get_formatted_timestamp()

    def set_dive_info(self, dive_info: dict):
        """
        Sets dive-related annotation data from passed dive_info dict.

        :param dict dive_info: A dictionary of information about the dive (imported from Dives.csv).
        """
        self.columns['Citation'] = dive_info['Citation'] if dive_info['Citation'] != NULL_VAL_STRING else ''
        self.columns['Repository'] = dive_info['DataProvider'].split(';')[0] + \
                                     ' | University of Hawaii Deep-sea Animal Research Center'
        self.columns['Locality'] = dive_info['Locality'].replace(',', ' |')
        self.columns['Ocean'] = dive_info['Ocean']
        self.columns['LargeMarineEcosystem'] = dive_info['LargeMarineEcosystem']
        self.columns['Country'] = dive_info['Country']
        self.columns['FishCouncilRegion'] = dive_info['FishCouncilRegion']
        self.columns['SurveyID'] = dive_info['SurveyID']
        self.columns['Vessel'] = dive_info['Vessel']
        self.columns['PI'] = dive_info['PI']
        self.columns['PIAffiliation'] = dive_info['PIAffiliation']
        self.columns['Purpose'] = dive_info['Purpose']
        self.columns['Station'] = dive_info['Station']
        self.columns['EventID'] = dive_info['EventID']
        self.columns['SamplingEquipment'] = dive_info['SamplingEquipment']
        self.columns['VehicleName'] = dive_info['VehicleName']
        self.columns['LocationAccuracy'] = \
            add_meters(dive_info['LocationAccuracy']) if dive_info['LocationAccuracy'] != 'NA' else ''
        self.columns['NavType'] = \
            'USBL' if dive_info['Vessel'] == 'Okeanos Explorer' or dive_info['Vessel'] == 'Nautilus' else 'NA'
        self.columns['WebSite'] = dive_info['WebSite']
        self.columns['DataProvider'] = dive_info['DataProvider']
        self.columns['DataContact'] = dive_info['DataContact']

    def set_concept_info(self, concepts: dict):
        """
        Sets annotation's concept info from saved concept dict.

        :param dict concepts: Dictionary of all locally saved concepts.
        """
        concept_name = self.annotation['concept']
        scientific_name = concepts[concept_name]['scientific_name']
        aphia_id = concepts[concept_name]['aphia_id']
        taxon_ranks = concepts[concept_name]['taxon_ranks']

        self.columns['ScientificName'] = scientific_name
        self.columns['VernacularName'] = concepts[concept_name]['vernacular_name']
        self.columns['TaxonRank'] = concepts[concept_name]['taxon_rank']
        self.columns['AphiaID'] = aphia_id

        if self.columns['AphiaID'] != NULL_VAL_INT:
            self.columns['LifeScienceIdentifier'] = f'urn:lsid:marinespecies.org:taxname:{aphia_id}'

        # Fill out the taxonomy from the taxon ranks
        if taxon_ranks != {}:
            for key in ['Kingdom', 'Phylum', 'Class', 'Subclass', 'Order', 'Suborder', 'Family',
                        'Subfamily', 'Genus', 'Subgenus', 'Species', 'Subspecies']:
                if key in taxon_ranks:
                    self.set_rank(rank=key, val=taxon_ranks[key])

        self.columns['ScientificNameAuthorship'] = concepts[concept_name]['authorship']
        self.columns['CombinedNameID'] = scientific_name

        if concepts[concept_name]['descriptors']:
            self.columns['Morphospecies'] = ' '.join(concepts[concept_name]['descriptors'])
            if self.columns['CombinedNameID'] != NULL_VAL_STRING:
                self.columns['CombinedNameID'] += f' {self.columns["Morphospecies"]}'
            else:
                self.columns['CombinedNameID'] = self.columns['Morphospecies']

        self.columns['Synonyms'] = ' | '.join(concepts[concept_name]['synonyms']) \
            if concepts[concept_name]['synonyms'] else NULL_VAL_STRING

    def set_rank(self, rank: str, val: str):
        """

        :param str rank:
        :param str val:
        """
        self.columns[rank] = val

    def set_media_type(self, media_type: str):
        self.columns['RecordType'] = media_type
        if self.columns['ScientificName'] != NULL_VAL_STRING:
            self.columns['IdentificationQualifier'] = \
                'ID by expert from video' if media_type == 'video observation' else 'ID by expert from image'

    def set_id_comments(self):
        id_comments = get_association(self.annotation, 'identity-certainty')
        if id_comments:
            id_comments = id_comments['link_value']
            id_comments = id_comments.split('; ')
            if 'maybe' in id_comments:
                self.columns['IdentificationQualifier'] = self.columns['IdentificationQualifier'] + ' | ID Uncertain'
                id_comments.remove('maybe')
            id_comments = ' | '.join(id_comments)
            self.columns['IdentificationComments'] = id_comments if id_comments != '' else NULL_VAL_STRING

    def set_pop_quantity_and_cat_abundance(self):
        pop_quantity = get_association(self.annotation, 'population-quantity')
        if pop_quantity:
            self.columns['IndividualCount'] = pop_quantity['link_value']
        elif self.columns['ScientificName'] != NULL_VAL_STRING:
            self.columns['IndividualCount'] = '1'
        else:
            self.columns['IndividualCount'] = NULL_VAL_INT
        cat_abundance = get_association(self.annotation, 'categorical-abundance')
        if cat_abundance:
            self.columns['CategoricalAbundance'] = cat_abundance['link_value']
            self.columns['IndividualCount'] = NULL_VAL_INT

    def set_size(self, warning_messages: list):
        min_size = NULL_VAL_INT
        max_size = NULL_VAL_INT
        size_str = NULL_VAL_STRING
        size_category = get_association(self.annotation, 'size')
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
                    warning_messages.append([
                        self.columns['SampleID'],
                        self.annotation["concept"],
                        self.annotation["observation_uuid"],
                        f'String not recognized as an established size category: {Color.BOLD}"{size_str}"{Color.END}'
                    ])
        self.columns['VerbatimSize'] = size_str
        self.columns['MinimumSize'] = min_size
        self.columns['MaximumSize'] = max_size

    def set_condition_comment(self, warning_messages: list):
        condition_comment = get_association(self.annotation, 'condition-comment')
        if condition_comment:
            if condition_comment['link_value'] in ['dead', 'Dead']:
                # flag warning
                warning_messages.append([
                    self.columns['SampleID'],
                    self.annotation["concept"],
                    self.annotation["observation_uuid"],
                    f'Dead animal reported'
                ])
                self.columns['Condition'] = 'Dead'
            else:
                self.columns['Condition'] = 'Damaged'
        else:
            self.columns['Condition'] = 'Live' if self.columns['ScientificName'] != NULL_VAL_STRING else NULL_VAL_STRING

    def set_comments_and_sample(self):
        # build occurrence remark string
        occurrence_remark = get_associations_list(self.annotation, 'occurrence-remark')
        remark_string = NULL_VAL_STRING
        if occurrence_remark:
            remark_list = []
            for remark in occurrence_remark:
                remark_list.append(remark['link_value'])
            remark_string = ' | '.join(remark_list)
        if self.columns['VerbatimSize'] != NULL_VAL_STRING:
            if remark_string != NULL_VAL_STRING:
                remark_string += ' | size is estimated greatest length of individual in cm. Size estimations placed into size category bins'
            else:
                remark_string = 'size is estimated greatest length of individual in cm. Size estimations placed into size category bins'
        sampled_by = get_association(self.annotation, 'sampled-by')
        if sampled_by:
            if remark_string != NULL_VAL_STRING:
                remark_string += f' | sampled by {sampled_by["to_concept"]}'
            else:
                remark_string = f'sampled by {sampled_by["to_concept"]}'
        sample_ref = get_association(self.annotation, 'sample-reference')
        if sample_ref:
            self.columns['TrackingID'] += f' | {sample_ref["link_value"]}'

        self.columns['OccurrenceComments'] = remark_string

    def set_cmecs_geo(self, cmecs_geo: str):
        self.columns['CMECSGeoForm'] = cmecs_geo

    def set_habitat(self, warning_messages):
        # habitat stuff
        primary = ''
        secondary = []
        s1 = get_association(self.annotation, 's1')
        if s1:
            primary = translate_substrate_code(s1['to_concept'])
            if not primary:
                # flag warning
                warning_messages.append([
                    self.columns['SampleID'],
                    self.annotation["concept"],
                    self.annotation["observation_uuid"],
                    f'{Color.RED}Missing s1 or could not parse substrate code:{Color.END} '
                    f'{Color.BOLD}{s1["to_concept"]}{Color.END}'
                ])
            else:
                self.columns['Habitat'] = f'primarily: {primary}'

        s2_records = get_associations_list(self.annotation, 's2')
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
                warning_messages.append([
                    self.columns['SampleID'],
                    self.annotation["concept"],
                    self.annotation["observation_uuid"],
                    f'Could not parse a substrate code from list {Color.BOLD}{secondary}{Color.END}'
                ])
            self.columns['Habitat'] = self.columns['Habitat'] + f' / secondary: {"; ".join(secondary)}'
        habitat_comment = get_association(self.annotation, 'habitat-comment')
        if habitat_comment:
            self.columns['Habitat'] = self.columns['Habitat'] + f' / comments: {habitat_comment["link_value"]}'

    def set_upon(self):
        """
        Checks if the item reported in 'upon' is in the list of accepted substrates - see translate_substrate_code
        """
        upon = get_association(self. annotation, 'upon')
        self.columns['UponIsCreature'] = False
        if upon:
            subs = translate_substrate_code(upon['to_concept'])
            if subs:
                self.columns['Substrate'] = subs
            else:
                # if the item in 'upon' is not in the substrate list, it must be upon another creature
                self.columns['Substrate'] = upon['to_concept']
                self.columns['UponIsCreature'] = True

    def set_id_ref(self):
        identity_reference = get_association(self.annotation, 'identity-reference')
        if identity_reference:
            self.columns['IdentityReference'] = int(identity_reference['link_value'])
        else:
            self.columns['IdentityReference'] = -1

    def set_temperature(self, warning_messages: list):
        if 'temperature_celsius' in self.annotation['ancillary_data']:
            self.columns['Temperature'] = round(self.annotation['ancillary_data']['temperature_celsius'], 4)
        else:
            self.columns['Temperature'] = NULL_VAL_INT
            # flag warning
            warning_messages.append([
                self.columns['SampleID'],
                self.annotation["concept"],
                self.annotation["observation_uuid"],
                'No temperature measurement included in this record'
            ])

    def set_salinity(self, warning_messages: list):
        if 'salinity' in self.annotation['ancillary_data']:
            self.columns['Salinity'] = round(self.annotation['ancillary_data']['salinity'], 4)
        else:
            self.columns['Salinity'] = NULL_VAL_INT
            # flag warning
            warning_messages.append([
                self.columns['SampleID'],
                self.annotation["concept"],
                self.annotation["observation_uuid"],
                'No salinity measurement included in this record'
            ])

    def set_oxygen(self, warning_messages: list):
        if 'oxygen_ml_l' in self.annotation['ancillary_data']:
            # convert to mL/L
            self.columns['Oxygen'] = round(self.annotation['ancillary_data']['oxygen_ml_l'] / 1.42903, 4)
        else:
            self.columns['Oxygen'] = NULL_VAL_INT
            # flag warning
            warning_messages.append([
                self.columns['SampleID'],
                self.annotation["concept"],
                self.annotation["observation_uuid"],
                'No oxygen measurement included in this record'
            ])

    def set_image_paths(self):
        images = self.annotation['image_references']
        image_paths = []
        for image in images:
            image_paths.append(image['url'].replace(
                'http://hurlstor.soest.hawaii.edu/imagearchive',
                'https://hurlimage.soest.hawaii.edu'))

        if len(image_paths) == 1:
            self.columns['ImageFilePath'] = image_paths[0]
        elif len(image_paths) > 1:
            if '.png' in image_paths[0]:
                self.columns['ImageFilePath'] = image_paths[0]
            else:
                self.columns['ImageFilePath'] = image_paths[1]

        highlight_image = get_association(self.annotation, 'guide-photo')
        if highlight_image and (highlight_image['to_concept'] == '1 best' or highlight_image['to_concept'] == '2 good'):
            self.columns['HighlightImageFilePath'] = self.columns['ImageFilePath']

        population_density = get_association(self.annotation, 'population-density')
        if population_density and population_density['link_value'] == 'dense':
            self.columns['HighlightImageFilePath'] = self.columns['ImageFilePath']
