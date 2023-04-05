from typing import Dict

from timestamp_processor import TimestampProcessor
from util.constants import NULL_VAL_STRING, HEADERS, NULL_VAL_INT
from util.functions import get_association, convert_username_to_name


class AnnotationRow:
    def __init__(self, annotation: Dict):
        self.columns = dict(zip(HEADERS, [NULL_VAL_STRING] * len(HEADERS)))
        self.annotation = annotation
        self.recorded_time = TimestampProcessor(self.annotation['recorded_timestamp'])
        self.observation_time = TimestampProcessor(self.annotation['observation_timestamp'])

    def set_simple_static_data(self):
        self.columns['VARSConceptName'] = self.annotation['concept']
        self.columns['TrackingID'] = self.annotation['observation_uuid']
        self.columns['AphiaID'] = NULL_VAL_INT
        self.columns['IdentifiedBy'] = convert_username_to_name(self.annotation['observer'])
        self.columns['IdentificationDate'] = self.observation_time.timestamp.strftime('%Y-%m-%d')
        self.columns['IdentificationVerificationStatus'] = 1
        self.columns['Latitude'] = round(self.annotation['ancillary_data']['latitude'], 8)
        self.columns['Longitude'] = round(self.annotation['ancillary_data']['longitude'], 8)

        # these four values are hardcoded for now, keeping columns in case of future update
        self.columns['SampleAreaInSquareMeters'] = NULL_VAL_INT
        self.columns['Density'] = NULL_VAL_INT
        self.columns['Cover'] = NULL_VAL_INT
        self.columns['WeightInKg'] = NULL_VAL_INT

    def set_sample_id(self, dive_name):
        self.columns['SampleID'] = dive_name.replace(' ',
                                                     '_') + '_' + self.recorded_time.get_formatted_timestamp()

    def set_dive_info(self, dive_info):
        self.columns['Citation'] = dive_info['Citation'] if dive_info['Citation'] != NULL_VAL_STRING else ''
        self.columns['Repository'] = dive_info['DataProvider'].split(';')[0] + \
                                     ' | University of Hawaii Deep-sea Animal Research Center'
        self.columns['Locality'] = dive_info['Locality'].replace(',', ' |')
        self.columns['Ocean'] = dive_info['Ocean']
        self.columns['LargeMarineEcosystem'] = dive_info['LargeMarineEcosystem']
        self.columns['Country'] = dive_info['Country']
        self.columns['FishCouncilRegion'] = dive_info['FishCouncilRegion']

    def set_concept_info(self, concepts):
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
                    self.set_rank(key, taxon_ranks[key])

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

    def set_rank(self, rank, val):
        self.columns[rank] = val

    def set_media_type(self, media_type):
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
