from unittest.mock import patch

from concept.concept import Concept
from concept.concept_handler import ConceptHandler
from util.constants import NULL_VAL_STRING
from test.data_for_tests import vars_responses, worms_responses


class MockResponse:
    def __init__(self, req_url, status_code):
        self.req_url = req_url
        self.status_code = status_code

    def json(self):
        if self.req_url == 'http://hurlstor.soest.hawaii.edu:8083/kb/v1/concept/Pennatulacea':
            return vars_responses['Pennatulacea']
        if self.req_url == 'http://hurlstor.soest.hawaii.edu:8083/kb/v1/concept/Demospongiae':
            return vars_responses['Demospongiae']
        if self.req_url == 'http://hurlstor.soest.hawaii.edu:8083/kb/v1/concept/Actinopterygii':
            return vars_responses['Actinopterygii']
        if self.req_url == 'https://www.marinespecies.org/rest/AphiaRecordsByName/Antipatharia?like=false&marine_only=true&offset=1':
            return worms_responses['Antipatharia']


def mocked_requests_get(*args, **kwargs):
    if args[0] is None:
        return MockResponse(None, 404)
    return MockResponse(args[0], 200)


class TestConceptHandler:
    """
    def test_worms_endpoints(self):
        res1 = requests.get('https://www.marinespecies.org/rest/AphiaRecordsByName/Demospongiae?like=true&marine_only=true&offset=1')
        res2 = requests.get('https://www.marinespecies.org/rest/AphiaClassificationByAphiaID/164811')
        res3 = requests.get('https://www.marinespecies.org/rest/AphiaVernacularsByAphiaID/164811')
        assert res1.ok
        assert res2.ok
        assert res3.ok

    def test_vars_endpoints(self):
        res1 = requests.get('http://hurlstor.soest.hawaii.edu:8083/kb/v1/phylogeny/up/Demospongiae')
        res2 = requests.get('http://hurlstor.soest.hawaii.edu:8083/kb/v1/concept/Demospongiae')
        assert res1.ok
        assert res2.ok
    """

    def test_init(self):
        test_concept = Concept('test concept')
        test_handler = ConceptHandler(test_concept)
        assert test_handler.concept == test_concept
        assert test_handler.phylum == ''
        assert test_handler.found_worms_match is False
        assert test_handler.unaccepted_names == []

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_fetch_worms_aphia_record_simple(self, mock_get):
        test_concept = Concept('Antipatharia')
        test_handler = ConceptHandler(test_concept)
        test_handler.fetch_worms_aphia_record()
        assert test_handler.found_worms_match is True
        assert test_concept.aphia_id == 22549
        assert test_concept.scientific_name == 'Antipatharia'
        assert test_concept.taxon_rank == 'Order'

    def test_fetch_worms_aphia_record_egg(self):
        test_concept1 = Concept('eggcase')
        test_concept2 = Concept('eggs')
        test_handler1 = ConceptHandler(test_concept1)
        test_handler2 = ConceptHandler(test_concept2)
        test_handler1.fetch_worms_aphia_record()
        test_handler2.fetch_worms_aphia_record()
        assert test_concept1.scientific_name == 'Animalia'
        assert test_concept1.descriptors == ['egg case']
        assert test_concept2.scientific_name == 'Animalia'
        assert test_concept2.descriptors == ['eggs']

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_fetch_worms_aphia_record_no_match(self, mock_get):
        assert 1 == 0  # todo

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_fetch_worms_aphia_record_extra_bits(self, mock_get):
        assert 1 == 0  # todo

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_find_parent_simple(self, mock_get):
        assert 1 == 0  # todo

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_find_parent_simple_fail(self, mock_get):
        assert 1 == 0  # todo

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_find_parent_slash_name(self, mock_get):
        assert 1 == 0  # todo

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_find_parent_slash_name_fail(self, mock_get):
        assert 1 == 0  # todo

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_find_accepted_record_single(self, mock_get):
        # one record
        assert 1 == 0  # todo

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_find_accepted_record_multiple(self, mock_get):
        # multiple records
        assert 1 == 0  # todo

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_find_accepted_record_no_match(self, mock_get):
        assert 1 == 0  # todo

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_check_status_accepted(self, mock_get):
        assert 1 == 0  # todo

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_check_status_unaccepted(self, mock_get):
        assert 1 == 0  # todo

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_fetch_worms_taxon_tree(self, mock_get):
        assert 1 == 0  # todo

    def test_fetch_worms_taxon_tree_egg(self):
        test_concept = Concept('eggcase')
        test_handler = ConceptHandler(test_concept)
        test_handler.fetch_worms_taxon_tree()
        assert test_concept.taxon_ranks == {'Kingdom': 'Animalia'}

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_fetch_worms_taxon_tree_no_match(self, mock_get):
        assert 1 == 0  # todo

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_fetch_vernaculars(self, mock_get):
        assert 1 == 0  # todo

    def test_fetch_vernaculars_egg(self):
        test_concept = Concept('eggcase')
        test_handler = ConceptHandler(test_concept)
        test_handler.fetch_vars_synonyms(warning_messages=[])
        assert test_concept.vernacular_names == NULL_VAL_STRING

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_fetch_vernaculars_none(self, mock_get):
        assert 1 == 0  # todo

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_fetch_vars_synonyms_simple(self, mock_get):
        test_concept = Concept('Actinopterygii')
        test_handler = ConceptHandler(test_concept)
        test_handler.fetch_vars_synonyms(warning_messages=[])
        assert test_concept.synonyms == ['Actinopteri']

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_fetch_vars_synonyms_complex(self, mock_get):
        # need to fetch info in alternate name
        # TODO
        assert 1 == 0  # todo

    def test_fetch_vars_synonyms_egg(self):
        test_concept = Concept('eggcase')
        test_handler = ConceptHandler(test_concept)
        test_handler.fetch_vars_synonyms(warning_messages=[])
        assert test_concept.synonyms == []

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_fetch_vars_synonyms_none(self, mock_get):
        test_concept = Concept('Demospongiae')
        test_handler = ConceptHandler(test_concept)
        test_handler.fetch_vars_synonyms(warning_messages=[])
        assert test_concept.synonyms == []