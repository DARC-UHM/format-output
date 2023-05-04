from unittest.mock import patch

from concept.concept import Concept
from concept.concept_handler import ConceptHandler
from util.constants import NULL_VAL_STRING
from test.data_for_tests import vars_responses, vars_concept_base_url


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

    def test_fetch_worms_taxon_tree_egg(self):
        test_concept = Concept('eggcase')
        test_handler = ConceptHandler(test_concept)
        test_handler.fetch_worms_taxon_tree()
        assert test_concept.taxon_ranks == {'Kingdom': 'Animalia'}

    def test_fetch_vernaculars_egg(self):
        test_concept = Concept('eggcase')
        test_handler = ConceptHandler(test_concept)
        test_handler.fetch_vars_synonyms(warning_messages=[])
        assert test_concept.vernacular_names == NULL_VAL_STRING

    def test_fetch_vars_synonyms_egg(self):
        test_concept = Concept('eggcase')
        test_handler = ConceptHandler(test_concept)
        test_handler.fetch_vars_synonyms(warning_messages=[])
        assert test_concept.synonyms == []

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
        pass

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_fetch_vars_synonyms_none(self, mock_get):
        test_concept = Concept('Demospongiae')
        test_handler = ConceptHandler(test_concept)
        test_handler.fetch_vars_synonyms(warning_messages=[])
        assert test_concept.synonyms == []