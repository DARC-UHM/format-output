from concept.concept import Concept
from concept.concept_handler import ConceptHandler


class TestConceptHandler:

    def test_init(self):
        test_concept = Concept('test concept')
        test_handler = ConceptHandler(test_concept)
        assert test_handler.concept == test_concept
        assert test_handler.phylum == ''
        assert test_handler.found_worms_match is False
        assert test_handler.unaccepted_names == []

    # todo how should these be tested? (all api calls)
