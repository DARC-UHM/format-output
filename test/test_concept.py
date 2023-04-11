from concept.concept import Concept
from test.data_for_tests import *
from util.constants import NULL_VAL_INT, NULL_VAL_STRING


class TestConcept:

    def test_init(self):
        test_concept = Concept('test_name')
        assert test_concept.concept_name == 'test_name'
        assert test_concept.aphia_id == NULL_VAL_INT
        assert test_concept.scientific_name == NULL_VAL_STRING
        assert test_concept.authorship == NULL_VAL_STRING
        assert test_concept.vernacular_names == NULL_VAL_STRING
        assert test_concept.synonyms == []
        assert test_concept.taxon_rank == NULL_VAL_STRING
        assert test_concept.taxon_ranks == {}
        assert test_concept.descriptors == []
        assert test_concept.concept_name_flag is False
        assert test_concept.concept_words == ['test_name']
        assert test_concept.concept_add_words == []
        assert test_concept.cf_flag == []
        assert test_concept.nr_flag == []
        assert test_concept.aff_flag == []
        assert test_concept.sp_flag is False

    def test_flatten_tree(self):
        test_concept = Concept('test_name')
        test_concept.flatten_taxa_tree(taxon_tree, test_concept.taxon_ranks)
        assert test_concept.taxon_ranks == flattened_tree

    def test_analyze_concept_name_simple(self):
        test_concept = Concept('Synaphobranchidae')
        assert test_concept.concept_words == ['Synaphobranchidae']
        assert test_concept.cf_flag == []
        assert test_concept.nr_flag == []
        assert test_concept.aff_flag == []
        assert test_concept.sp_flag is False

    def test_analyze_concept_name_cf_end(self):
        test_concept = Concept('Ceriantharia cf')
        assert test_concept.concept_words == ['NEED_PARENT']
        assert test_concept.cf_flag == ['Ceriantharia']
        assert test_concept.nr_flag == []
        assert test_concept.aff_flag == []
        assert test_concept.sp_flag is False

    def test_analyze_concept_name_cf_mid(self):
        test_concept = Concept('Iridogorgia splendens cf')
        assert test_concept.concept_words == ['Iridogorgia']
        assert test_concept.cf_flag == ['splendens']
        assert test_concept.nr_flag == []
        assert test_concept.aff_flag == []
        assert test_concept.sp_flag is False

    def test_analyze_concept_name_sp_one(self):
        test_concept = Concept('Hemicorallium sp')
        assert test_concept.concept_words == ['Hemicorallium']
        assert test_concept.descriptors == []
        assert test_concept.cf_flag == []
        assert test_concept.nr_flag == []
        assert test_concept.aff_flag == []
        assert test_concept.sp_flag is True

    def test_analyze_concept_name_sp_two(self):
        test_concept = Concept('Hyalonema (Corynonema) sp')
        assert test_concept.concept_words == ['Hyalonema', '(Corynonema)']
        assert test_concept.descriptors == []
        assert test_concept.cf_flag == []
        assert test_concept.nr_flag == []
        assert test_concept.aff_flag == []
        assert test_concept.sp_flag is True

    def test_analyze_concept_name_nr_one(self):
        test_concept = Concept('Farrea nr occa')
        assert test_concept.concept_words == ['Farrea']
        assert test_concept.cf_flag == []
        assert test_concept.nr_flag == ['occa']
        assert test_concept.aff_flag == []
        assert test_concept.sp_flag is False

    def test_analyze_concept_name_nr_two(self):
        test_concept = Concept('Farrea nr occa erecta')
        assert test_concept.concept_words == ['Farrea']
        assert test_concept.cf_flag == []
        assert test_concept.nr_flag == ['occa', 'erecta']
        assert test_concept.aff_flag == []
        assert test_concept.sp_flag is False

    def test_analyze_concept_name_aff_one(self):
        test_concept = Concept('Genus aff species')
        assert test_concept.concept_words == ['Genus']
        assert test_concept.cf_flag == []
        assert test_concept.nr_flag == []
        assert test_concept.aff_flag == ['species']
        assert test_concept.sp_flag is False

    def test_analyze_concept_name_aff_two(self):
        test_concept = Concept('Genus aff species sub')
        assert test_concept.concept_words == ['Genus']
        assert test_concept.cf_flag == []
        assert test_concept.nr_flag == []
        assert test_concept.aff_flag == ['species', 'sub']
        assert test_concept.sp_flag is False

    def test_analyze_concept_name_new_sp(self):
        test_concept = Concept('Porites n sp')
        assert test_concept.concept_words == ['Porites']
        assert test_concept.cf_flag == []
        assert test_concept.nr_flag == []
        assert test_concept.aff_flag == []
        assert test_concept.descriptors == ['Undescribed species']
        assert test_concept.sp_flag is False

    def test_analyze_concept_name_new_sub_sp(self):
        test_concept = Concept('Porites (n subgenus) n sp')
        assert test_concept.concept_words == ['Porites']
        assert test_concept.cf_flag == []
        assert test_concept.nr_flag == []
        assert test_concept.aff_flag == []
        assert test_concept.descriptors == ['Undescribed subgenus, undescribed species']
        assert test_concept.sp_flag is False

    def test_analyze_concept_name_new_gen(self):
        test_concept = Concept('Poritidae n gen')
        assert test_concept.concept_words == ['Poritidae']
        assert test_concept.cf_flag == []
        assert test_concept.nr_flag == []
        assert test_concept.aff_flag == []
        assert test_concept.descriptors == ['Undescribed genus']
        assert test_concept.sp_flag is False

    def test_load_from_record(self):
        test_concept = Concept('Illex coindetii')
        test_concept.load_from_record(aphia_record)
        assert test_concept.concept_name == 'Illex coindetii'
        assert test_concept.aphia_id == aphia_record['AphiaID']
        assert test_concept.scientific_name == aphia_record['scientificname']
        assert test_concept.authorship == aphia_record['authority']
        assert test_concept.taxon_rank == aphia_record['rank']
        assert test_concept.descriptors == []
        assert test_concept.cf_flag == []
        assert test_concept.nr_flag == []
        assert test_concept.aff_flag == []
        assert test_concept.sp_flag is False

