from util.functions import *
from util.constants import ROOTS
from test.data_test_functions import *


class TestFunctions:

    def test_get_association(self):
        test_obj = get_association(annotations[0], 'upon')
        assert test_obj == {
            "uuid": "c4eaa100-4bee-46a9-0f65-6525fb69d41e",
            "link_name": "upon",
            "to_concept": "sed",
            "link_value": "nil",
            "mime_type": "text/plain"
        }

    def test_get_association_none(self):
        test_obj = get_association(annotations[0], 'test')
        assert test_obj == {}

    def test_get_associations_list(self):
        test_list = get_associations_list(annotations[1], 's2')
        assert test_list == [{
            "uuid": "a1c3990e-3566-4832-4d6d-6e4fb25dd41e",
            "link_name": "s2",
            "to_concept": "mantra",
            "link_value": "nil",
            "mime_type": "text/plain"
        }]

    def test_get_associations_list_none(self):
        test_list = get_associations_list(annotations[0], 's2')
        assert test_list == []

    def test_grain_size(self):
        test_size = grain_size(annotations[1]['associations'][1]['to_concept'])
        print(test_size)
        assert test_size == 11

    def test_grain_size_no_match(self):
        root_index = grain_size(no_match)
        assert root_index == len(ROOTS)

    def test_get_date_time(self):
        date_time = get_date_and_time(list_data)
        assert date_time == datetime(2014, 9, 8, 0, 33, 49)

    def test_parse_datetime_micro(self):
        date_time = parse_datetime('2014-09-05T14:08:41.492Z')
        assert date_time == datetime(2014, 9, 5, 14, 8, 41, 492000)

    def test_parse_datetime_no_micro(self):
        date_time = parse_datetime('2014-09-05T14:08:41Z')
        assert date_time == datetime(2014, 9, 5, 14, 8, 41)

    def test_extract_time_no_micro(self):
        date_time = extract_time(annotations[0])
        assert date_time == datetime(2014, 9, 5, 20, 6, 26)

    def test_extract_time_round_up(self):
        date_time = extract_time(annotations[1])
        assert date_time == datetime(2014, 9, 5, 14, 37, 58)

    def test_extract_time_round_down(self):
        date_time = extract_time(annotations[2])
        assert date_time == datetime(2014, 9, 20, 14, 13, 23)

    def test_extract_uuid(self):
        uuid = extract_uuid(annotations[2])
        assert uuid == '080118db-baa2-468a-d06a-144249c1d41e'

    def test_add_meters_no_m(self):
        accuracy = add_meters('50')
        assert accuracy == '50m'

    def test_add_meters_m(self):
        accuracy = add_meters('50m')
        assert accuracy == '50m'

    def test_convert_username_to_name(self):
        test_name = convert_username_to_name('SarahBingo')
        assert test_name == 'Bingo, Sarah'

    def test_convert_username_to_name_fail(self):
        test_name = convert_username_to_name('Sarahbingo')
        assert test_name == 'Sarahbingo'

    def test_translate_substrate_code_same(self):
        test_translated = translate_substrate_code('pebble')
        assert test_translated == 'pebble'

    def test_translate_substrate_code_tube(self):
        test_translated = translate_substrate_code('tube')
        assert test_translated == 'Animal-made tube'

    def test_translate_substrate_code_simple(self):
        test_translated = translate_substrate_code('bed')
        assert test_translated == 'bedrock'

    def test_translate_substrate_code_complex1(self):
        test_translated = translate_substrate_code('pibed')
        assert test_translated == 'pillow lava formation of bedrock'

    def test_translate_substrate_code_complex2(self):
        test_translated = translate_substrate_code('sedmn')
        assert test_translated == 'sediment with manganese crust'

    def test_translate_substrate_code_complex3(self):
        test_translated = translate_substrate_code('boucre')
        assert test_translated == 'boulder crevice'

    def test_translate_substrate_code_fail(self):
        test_translated = translate_substrate_code('hehehe')
        assert test_translated == ''

    def test_collapse_id_records(self):
        test_dupes_removed = collapse_id_records(sample_report_records)
        assert test_dupes_removed == 1
        assert sample_report_records == sample_report_records_collapsed

    def test_collapse_id_records_none(self):
        test_dupes_removed = collapse_id_records(sample_report_records_collapsed)
        assert test_dupes_removed == 0
        assert sample_report_records_collapsed == sample_report_records_collapsed

    def test_find_associated_taxa_host_before(self):
        """ Check for a host recorded before associate """
        find_associated_taxa(report_records=sample_records_for_associates, concepts=sample_concepts,
                             warning_messages=[])
        assert sample_records_for_associates[18][ASSOCIATED_TAXA] == 'Ophiacanthidae'
        assert 'associate touching host' in sample_records_for_associates[18][OCCURRENCE_COMMENTS]

    def test_find_associated_taxa_host_same_time(self):
        """ Check for a host recorded at the same time as the associate """
        find_associated_taxa(report_records=sample_records_for_associates, concepts=sample_concepts,
                             warning_messages=[])
        assert sample_records_for_associates[14][ASSOCIATED_TAXA] == 'Ophiacanthidae'
        assert 'associate touching host' in sample_records_for_associates[14][OCCURRENCE_COMMENTS]

    def test_find_associated_taxa_host_future(self):
        """ Check for a host recorded after the associate (fail) """
        warnings = []
        find_associated_taxa(report_records=sample_records_for_associates, concepts=sample_concepts,
                             warning_messages=warnings)
        assert sample_records_for_associates[2][ASSOCIATED_TAXA] == NULL_VAL_STRING
        print(warnings)
        assert 'Upon not found in previous records' in warnings[1][3]

    def test_find_associated_taxa_prev_dive(self):
        """ Associate not found in current dive, but exists in previous dive (fail) """
        warnings = []
        find_associated_taxa(report_records=sample_records_for_associates, concepts=sample_concepts,
                             warning_messages=warnings)
        assert sample_records_for_associates[1][ASSOCIATED_TAXA] == NULL_VAL_STRING
        assert 'Upon not found in previous records' in warnings[0][3]

    def test_find_associated_taxa_host_same_concept(self):
        """ Check for a record where the host and the associate are the same concept """
        find_associated_taxa(report_records=sample_records_for_associates, concepts=sample_concepts,
                             warning_messages=[])
        assert sample_records_for_associates[3][ASSOCIATED_TAXA] == 'Narella sp.'
        assert 'associate touching host' in sample_records_for_associates[3][OCCURRENCE_COMMENTS]

    def test_find_associated_taxa_multiple_associates(self):
        """ Check for a record where multiple associates are on the same host """
        find_associated_taxa(report_records=sample_records_for_associates, concepts=sample_concepts,
                             warning_messages=[])
        assert sample_records_for_associates[7][ASSOCIATED_TAXA] == 'Keratoisididae unbranched | Alternatipathes cf. alternata'
        assert 'associate touching host' in sample_records_for_associates[7][OCCURRENCE_COMMENTS]

    def test_find_associated_taxa_upon_not_in_concepts(self):
        """ Check for an 'upon' that is not in concepts """
        warnings = []
        find_associated_taxa(report_records=sample_records_for_associates, concepts=sample_concepts,
                             warning_messages=warnings)
        assert sample_records_for_associates[20][ASSOCIATED_TAXA] == NULL_VAL_STRING
        assert 'My Special Concept' in warnings[2][3]

    def test_find_associated_taxa_upon_over_one_min(self):
        """ Check for an 'upon' that is reported over one minute after its host """
        warnings = []
        find_associated_taxa(report_records=sample_records_for_associates, concepts=sample_concepts,
                             warning_messages=warnings)
        assert sample_records_for_associates[18][ASSOCIATED_TAXA] == 'Ophiacanthidae'
        assert 'greater than 1 minute' in warnings[3][3]

    def test_find_associated_taxa_upon_over_five_mins(self):
        """ Check for an 'upon' that is reported over five minutes after its host """
        warnings = []
        find_associated_taxa(report_records=sample_records_for_associates, concepts=sample_concepts,
                             warning_messages=warnings)
        assert sample_records_for_associates[18][ASSOCIATED_TAXA] == 'Ophiacanthidae'
        assert 'greater than 5 minutes' in warnings[4][3]
