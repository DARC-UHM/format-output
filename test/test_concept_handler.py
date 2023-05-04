from unittest.mock import patch

from concept.concept import Concept
from concept.concept_handler import ConceptHandler
from util.constants import NULL_VAL_STRING
from test.data_for_tests import vars_responses, worms_responses


class MockResponse:
    def __init__(self, req_url):
        self.req_url = req_url
        self.status_code = 404 if 'NO_MATCH' in req_url or 'encrusting' in req_url else 200

    def json(self):
        match self.req_url:
            case 'NO_MATCH':
                return {}
            case 'http://hurlstor.soest.hawaii.edu:8083/kb/v1/concept/Pennatulacea':
                return vars_responses['Pennatulacea']
            case 'http://hurlstor.soest.hawaii.edu:8083/kb/v1/concept/Demospongiae':
                return vars_responses['Demospongiae']
            case 'http://hurlstor.soest.hawaii.edu:8083/kb/v1/concept/Actinopterygii':
                return vars_responses['Actinopterygii']
            case 'https://www.marinespecies.org/rest/AphiaRecordsByName/Antipatharia?like=false&marine_only=true&offset=1':
                return worms_responses['Antipatharia']
            case 'https://www.marinespecies.org/rest/AphiaRecordsByName/Demospongiae?like=false&marine_only=true&offset=1':
                return worms_responses['Demospongiae']
            case 'http://hurlstor.soest.hawaii.edu:8083/kb/v1/phylogeny/up/Demospongiae' | \
                 'http://hurlstor.soest.hawaii.edu:8083/kb/v1/phylogeny/up/Demospongiae cf':
                return vars_responses['Demospongiae phylogeny']
            case 'http://hurlstor.soest.hawaii.edu:8083/kb/v1/phylogeny/up/Pennatula':
                return vars_responses['Pennatula phylogeny']
            case 'http://hurlstor.soest.hawaii.edu:8083/kb/v1/phylogeny/up/Ptilella':
                return vars_responses['Ptilella phylogeny']
            case 'https://www.marinespecies.org/rest/AphiaRecordsByName/Stolonifera?like=false&marine_only=true&offset=1':
                return worms_responses['Stolonifera']
            case 'http://hurlstor.soest.hawaii.edu:8083/kb/v1/phylogeny/up/Stolonifera':
                return vars_responses['Stolonifera phylogeny']
            case 'https://www.marinespecies.org/rest/AphiaRecordsByName/Malacalcyonacea?like=false&marine_only=true&offset=1':
                return worms_responses['Malacalcyonacea']
        return None


def mocked_requests_get(*args, **kwargs):
    return MockResponse(args[0])


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
        test_concept = Concept('NO_MATCH')
        test_handler = ConceptHandler(test_concept)
        test_handler.fetch_worms_aphia_record()
        assert test_handler.found_worms_match is False

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_fetch_worms_aphia_record_extra_bits(self, mock_get):
        test_concept = Concept('Demospongiae encrusting')
        test_handler = ConceptHandler(test_concept)
        test_handler.fetch_worms_aphia_record()
        assert test_handler.found_worms_match is True
        assert test_concept.aphia_id == 164811
        assert test_concept.scientific_name == 'Demospongiae'
        assert test_concept.taxon_rank == 'Class'

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_find_parent_simple(self, mock_get):
        test_concept = Concept('Demospongiae cf')
        ConceptHandler(test_concept)
        assert test_concept.concept_words == ['Porifera']

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_find_parent_simple_fail(self, mock_get):
        test_concept = Concept('NO_MATCH cf')
        ConceptHandler(test_concept)
        assert test_concept.concept_words == ['NA']

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_find_parent_slash_name(self, mock_get):
        test_concept = Concept('Ptilella/Pennatula')
        ConceptHandler(test_concept)
        assert test_concept.concept_words == ['Pennatulidae']

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_find_parent_slash_name_fail(self, mock_get):
        test_concept = Concept('NO_MATCH/Pennatula')
        ConceptHandler(test_concept)
        assert test_concept.concept_words == ['NEED_PARENT']

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_find_accepted_record(self, mock_get):
        # multiple records (we already check single record in test_fetch_worms_aphia_record)
        test_concept = Concept('Stolonifera')
        test_handler = ConceptHandler(test_concept)
        test_handler.fetch_worms_aphia_record()
        assert test_handler.found_worms_match is True
        assert test_concept.aphia_id == 1609357
        assert test_concept.scientific_name == 'Malacalcyonacea'
        assert test_concept.taxon_rank == 'Order'

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_find_accepted_record_no_match(self, mock_get):
        test_concept = Concept('Stolonifera')
        test_handler = ConceptHandler(test_concept)
        test_handler.fetch_worms_aphia_record()
        assert test_handler.found_worms_match is True
        assert test_concept.aphia_id == 1609357
        assert test_concept.scientific_name == 'Malacalcyonacea'
        assert test_concept.taxon_rank == 'Order'

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_check_status_accepted(self, mock_get):
        pass  # todo

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_check_status_unaccepted(self, mock_get):
        pass  # todo

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_fetch_worms_taxon_tree(self, mock_get):
        pass  # todo

    def test_fetch_worms_taxon_tree_egg(self):
        test_concept = Concept('eggcase')
        test_handler = ConceptHandler(test_concept)
        test_handler.fetch_worms_taxon_tree()
        assert test_concept.taxon_ranks == {'Kingdom': 'Animalia'}

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_fetch_worms_taxon_tree_no_match(self, mock_get):
        pass  # todo

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_fetch_vernaculars(self, mock_get):
        pass  # todo

    def test_fetch_vernaculars_egg(self):
        test_concept = Concept('eggcase')
        test_handler = ConceptHandler(test_concept)
        test_handler.fetch_vars_synonyms(warning_messages=[])
        assert test_concept.vernacular_names == NULL_VAL_STRING

    @patch('concept.concept_handler.requests.get', side_effect=mocked_requests_get)
    def test_fetch_vernaculars_none(self, mock_get):
        pass  # todo

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
        pass  # todo

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