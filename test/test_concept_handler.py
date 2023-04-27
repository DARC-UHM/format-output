from concept.concept import Concept
from concept.concept_handler import ConceptHandler
import pytest
import requests

from util.constants import NULL_VAL_STRING


class MockResponse:

    @staticmethod
    def json():
        return {'test': ':)'}


class TestConceptHandler:

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


"""
    def test_fetch_vars_synonyms(self, monkeypatch):
        def mock_get(*args, **kwargs):
            return MockResponse()

        monkeypatch.setattr(requests, "get", mock_get)

        test_concept = Concept('Poliopogon spA')
        test_handler = ConceptHandler(test_concept)
        test_handler.fetch_vars_synonyms(warning_messages=[])
        print(test_concept.scientific_name)
        assert 1 == 0
"""
