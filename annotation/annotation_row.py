from typing import Dict

from timestamp_processor import TimestampProcessor
from concept.concept import Concept
from concept.concept_handler import ConceptHandler
from util.constants import NULL_VAL_STRING, HEADERS, NULL_VAL_INT


class AnnotationRow:
    def __init__(self, annotation: Dict):
        self.columns = dict(zip(HEADERS, [NULL_VAL_STRING] * len(HEADERS)))
        self.annotation = annotation
        self.timestamp_processor = TimestampProcessor(self.annotation['recorded_timestamp'])

        # just populate these now so don't have to worry about it later
        self.columns['AphiaID'] = NULL_VAL_INT

        # these four values are hardcoded for now, keeping columns in case of future update
        self.columns['SampleAreaInSquareMeters'] = NULL_VAL_INT
        self.columns['Density'] = NULL_VAL_INT
        self.columns['Cover'] = NULL_VAL_INT
        self.columns['WeightInKg'] = NULL_VAL_INT

    def populate_static_data(self):
        self.columns['VARSConceptName'] = self.annotation['concept']
        self.columns['TrackingID'] = self.annotation['observation_uuid']

    def set_sample_id(self, dive_name):
        self.columns['SampleID'] = dive_name.replace(' ',
                                                     '_') + '_' + self.timestamp_processor.get_formatted_timestamp()

    def set_dive_info(self, dive_info):
        self.columns['Citation'] = dive_info['Citation'] if dive_info['Citation'] != NULL_VAL_STRING else ''
        self.columns['Repository'] = dive_info['DataProvider'].split(';')[0] + \
            ' | University of Hawaii Deep-sea Animal Research Center'

    def set_concept_info(self, concepts):
        concept_name = self.annotation['concept']

        self.columns['ScientificName'] = concepts[concept_name]['scientific_name']
        self.columns['VernacularName'] = concepts[concept_name]['vernacular_name']
        self.columns['TaxonRank'] = concepts[concept_name]['taxon_rank']
        self.columns['AphiaID'] = concepts[concept_name]['aphia_id']

        scientific_name =
        aphia_id =
        authorship = concepts[concept_name]['authorship']
        synonyms = ' | '.join(concepts[concept_name]['synonyms']) if concepts[concept_name]['synonyms'] \
            else NULL_VAL_STRING
        tax_rank =
        taxon_ranks = concepts[concept_name]['taxon_ranks']
        descriptors = concepts[concept_name]['descriptors']
        vernacular_name =

        # Fill out the taxonomy from the taxon ranks
        if taxon_ranks != {}:
            for key in ['Kingdom', 'Phylum', 'Class', 'Subclass', 'Order',
                        'Suborder', 'Family', 'Subfamily', 'Genus',
                        'Subgenus', 'Species', 'Subspecies']:
                if key in taxon_ranks:
                    annotation_row.set_rank(key, taxon_ranks[key])

    def set_rank(self, rank, val):
        self.columns[rank] = val
