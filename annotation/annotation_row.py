from typing import Dict
from util.constants import NULL_VAL_STRING, HEADERS


class AnnotationRow:

    def __init__(self):
        self.columns = dict(zip(HEADERS, [NULL_VAL_STRING] * len(HEADERS)))

    def update_sample_id(self, dive_name, timestamp):
        self.columns['SampleID'] = dive_name.replace(' ', '_') + '_' + timestamp

    def update_tracking_id(self, tracking_id):
        self.columns['TrackingID'] = tracking_id

    def update_repo(self, data_provider):
        self.columns['Repository'] = data_provider + ' | University of Hawaii Deep-sea Animal Research Center'
