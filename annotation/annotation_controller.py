from typing import Dict
from timestamp_processor import TimestampProcessor

from annotation_row import AnnotationRow
from concept.concept_handler import ConceptHandler
from util.functions import *
from concept.concept import Concept


class AnnotationController:
    def __init__(self, timestamp_processor: TimestampProcessor):
        self.timestamp_processor = timestamp_processor
        self.warning_messages = []

    def load_annotation_data(self, dive_name: str, dive_admin_info: Dict, annotation: Dict, saved_concept: Dict):
        annotation_row = AnnotationRow(HEADERS)
        self.timestamp_processor.load_time(annotation['recorded_timestamp'])
        annotation_row.update_sample_id(dive_name, self.timestamp_processor.get_formatted_timestamp())
        annotation_row.update_tracking_id(annotation['observation_uuid'])
        annotation_row.update_repo(dive_admin_info['DataProvider'].split(';')[0])

        aphia_id = NULL_VAL_INT
        tax_rank = NULL_VAL_STRING
        scientific_name = NULL_VAL_STRING
        authorship = NULL_VAL_STRING
        descriptors = []
        taxon_ranks = {}

        concept_name = annotation['concept']

        # If concept name not in save concepts file, searches WoRMS
        if concept_name != 'none':
            if not saved_concept:
                concept = Concept(concept_name)
                cons_handler = ConceptHandler()
                cons_handler.fetch_worms_aphia_record(concept)
                fetch_worms_aphia_classification(concept)
                saved_concept = {
                    'scientific_name': concept.scientific_name,
                    'aphia_id': concept.aphia_id,
                    'authorship': concept.authorship,
                    'taxon_ranks': concept.taxon_ranks,
                    'descriptors': concept.descriptors
                }
                if concept.cf_flag:
                    self.warning_messages.append([
                        dive_name,
                        annotation['observation_uuid'],
                        annotation['concept'],
                        self.timestamp_processor.load_time(annotation['recorded_timestamp']),
                        'Concept name',
                        concept_name,
                        0,
                        'Concept name contains cf; requires manual review for placement.'
                    ])
                if concept.concept_name_flag:
                    self.warning_messages.append([
                        dive_name,
                        annotation['observation_uuid'],
                        annotation['concept'],
                        self.timestamp_processor.load_time(annotation['recorded_timestamp']),
                        'Concept name',
                        concept_name,
                        2,
                        'No words in concept match any object in WoRMS database. Check for spelling errors and fix.'
                    ])
                # concepts_from_worms += 1
            else:
                # concepts_from_save += 1
                pass
