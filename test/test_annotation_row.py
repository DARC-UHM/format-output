from annotation.annotation_row import AnnotationRow
from annotation.timestamp_processor import TimestampProcessor
from test.data_for_tests import annotations, dive_dict, concepts
from util.constants import HEADERS, NULL_VAL_STRING, NULL_VAL_INT


class TestAnnotationRow:

    def test_init(self):
        test_row = AnnotationRow(annotations[0])
        i = 0
        for key in test_row.columns.keys():
            assert key == HEADERS[i]
            i += 1
        for val in test_row.columns.values():
            assert val == NULL_VAL_STRING
        assert test_row.annotation == {
            "observation_uuid": "0059f860-4799-485f-c06c-5830e5ddd31e",
            "concept": "Chaceon quinquedens",
            "observer": "NikkiCunanan",
            "observation_timestamp": "2022-11-17T21:26:14.245Z",
            "video_reference_uuid": "cd74c489-6336-4b97-89a6-f151872f282b",
            "imaged_moment_uuid": "aa7c743e-99ba-4b65-c16c-aeb3585dc91e",
            "elapsed_time_millis": 0,
            "recorded_timestamp": "2014-09-05T20:06:26Z",
            "group": "ROV",
            "associations": [
                {
                    "uuid": "08f0563b-090e-417e-0e68-c314fb69d41e",
                    "link_name": "s1",
                    "to_concept": "sed",
                    "link_value": "nil",
                    "mime_type": "text/plain"
                },
                {
                    "uuid": "c4eaa100-4bee-46a9-0f65-6525fb69d41e",
                    "link_name": "upon",
                    "to_concept": "sed",
                    "link_value": "nil",
                    "mime_type": "text/plain"
                }
            ]
        }
        assert test_row.recorded_time.timestamp == \
               TimestampProcessor(test_row.annotation['recorded_timestamp']).timestamp
        assert test_row.observation_time.timestamp == \
               TimestampProcessor(test_row.annotation['observation_timestamp']).timestamp

    def test_simple_static_data(self):
        test_row = AnnotationRow(annotations[1])
        test_row.set_simple_static_data()
        assert test_row.columns['VARSConceptName'] == 'Paralepididae'
        assert test_row.columns['TrackingID'] == '0d9133d7-1d49-47d5-4b6d-6e4fb25dd41e'
        assert test_row.columns['AphiaID'] == NULL_VAL_INT
        assert test_row.columns['IdentifiedBy'] == 'Putts, Meagan'
        assert test_row.columns['IdentificationDate'] == test_row.observation_time.timestamp.strftime('%Y-%m-%d')
        assert test_row.columns['IdentificationVerificationStatus'] == 1
        assert test_row.columns['Latitude'] == round(38.793148973388, 8)
        assert test_row.columns['Longitude'] == round(-72.992393976812, 8)
        assert test_row.columns['DepthInMeters'] == round(668.458984375, 3)
        assert test_row.columns['MinimumDepthInMeters'] == round(668.458984375, 3)
        assert test_row.columns['MaximumDepthInMeters'] == round(668.458984375, 3)
        assert test_row.columns['DepthMethod'] == 'reported'
        assert test_row.columns['ObservationDate'] == test_row.recorded_time.timestamp.strftime('%Y-%m-%d')
        assert test_row.columns['ObservationTime'] == test_row.recorded_time.timestamp.strftime('%H:%M:%S')
        assert test_row.columns['VerbatimLatitude'] == 38.793148973388
        assert test_row.columns['VerbatimLongitude'] == -72.992393976812
        assert test_row.columns['OtherData'] == 'CTD'
        # skip checking 'Modified' column (initialized to current time)
        assert test_row.columns['Reporter'] == 'Bingo, Sarah'
        assert test_row.columns['ReporterEmail'] == 'sarahr6@hawaii.edu'
        assert test_row.columns['EntryDate'] == ''
        assert test_row.columns['SampleAreaInSquareMeters'] == NULL_VAL_INT
        assert test_row.columns['Density'] == NULL_VAL_INT
        assert test_row.columns['Cover'] == NULL_VAL_INT
        assert test_row.columns['WeightInKg'] == NULL_VAL_INT
        assert test_row.columns['SampleAreaInSquareMeters'] == NULL_VAL_INT
        assert test_row.columns['Density'] == NULL_VAL_INT
        assert test_row.columns['WeightInKg'] == NULL_VAL_INT

    def test_set_sample_id(self):
        test_row = AnnotationRow(annotations[1])
        test_row.set_sample_id('my test dive :)')
        assert test_row.columns['SampleID'] == 'my_test_dive_:)_' + test_row.recorded_time.get_formatted_timestamp()

    def test_set_dive_info(self):
        test_row = AnnotationRow(annotations[1])
        test_row.set_dive_info(dive_dict)
        assert test_row.columns['Citation'] == ''
        assert test_row.columns['Repository'] == \
               'Ocean Exploration Trust | University of Hawaii Deep-sea Animal Research Center'
        assert test_row.columns['Locality'] == \
               'Papah_naumoku_kea Marine National Monument (PMNM) | Northwestern Hawaiian Islands | Unnamed Seamount A'
        assert test_row.columns['Ocean'] == 'North Pacific'
        assert test_row.columns['LargeMarineEcosystem'] == 'Insular Pacific-Hawaiian'
        assert test_row.columns['Country'] == 'USA'
        assert test_row.columns['FishCouncilRegion'] == 'Western Pacific'
        assert test_row.columns['SurveyID'] == 'NA134'
        assert test_row.columns['Vessel'] == 'Nautilus'
        assert test_row.columns['PI'] == 'Kelley, Christopher; Kosaki, Randy; Orcutt, Beth; Petruncio, Emil'
        assert test_row.columns['PIAffiliation'] == 'NA'
        assert test_row.columns['Purpose'] == 'Document whether these underwater mountains support vibrant coral ' \
                                              'and sponge communities like others in the region'
        assert test_row.columns['Station'] == 'NA134-H1884'
        assert test_row.columns['EventID'] == 'NA134-H1884'
        assert test_row.columns['SamplingEquipment'] == 'ROV'
        assert test_row.columns['VehicleName'] == 'Hercules'
        assert test_row.columns['LocationAccuracy'] == '50m'
        assert test_row.columns['NavType'] == 'USBL'
        assert test_row.columns['WebSite'] == 'https://nautiluslive.org/cruise/na134'
        assert test_row.columns['DataProvider'] == 'Ocean Exploration Trust; University of Hawaiʻi'
        assert test_row.columns['DataContact'] == 'Bingo, Sarah; sarahr6@hawaii.edu'

    def test_set_concept_info_no_descriptors(self):
        test_row = AnnotationRow(annotations[1])
        test_row.set_concept_info(concepts)
        assert test_row.columns['ScientificName'] == 'Paralepididae'
        assert test_row.columns['VernacularName'] == 'barracudinas'
        assert test_row.columns['TaxonRank'] == 'Family'
        assert test_row.columns['AphiaID'] == 125447
        assert test_row.columns['LifeScienceIdentifier'] == 'urn:lsid:marinespecies.org:taxname:125447'
        assert test_row.columns['Kingdom'] == 'Animalia'
        assert test_row.columns['Phylum'] == 'Chordata'
        assert test_row.columns['Class'] == 'Teleostei'
        assert test_row.columns['Subclass'] == NULL_VAL_STRING
        assert test_row.columns['Order'] == 'Aulopiformes'
        assert test_row.columns['Suborder'] == NULL_VAL_STRING
        assert test_row.columns['Family'] == 'Paralepididae'
        assert test_row.columns['Subfamily'] == NULL_VAL_STRING
        assert test_row.columns['Genus'] == NULL_VAL_STRING
        assert test_row.columns['Subgenus'] == NULL_VAL_STRING
        assert test_row.columns['Species'] == NULL_VAL_STRING
        assert test_row.columns['Subspecies'] == NULL_VAL_STRING
        assert test_row.columns['ScientificNameAuthorship'] == 'Bonaparte, 1835'
        assert test_row.columns['CombinedNameID'] == 'Paralepididae'
        assert test_row.columns['Morphospecies'] == NULL_VAL_STRING
        assert test_row.columns['Synonyms'] == NULL_VAL_STRING

    def test_set_concept_info_descriptors(self):
        test_row = AnnotationRow(annotations[3])
        test_row.set_concept_info(concepts)
        assert test_row.columns['ScientificName'] == 'Demospongiae'
        assert test_row.columns['VernacularName'] == 'demosponges | horny sponges'
        assert test_row.columns['TaxonRank'] == 'Class'
        assert test_row.columns['AphiaID'] == 164811
        assert test_row.columns['LifeScienceIdentifier'] == 'urn:lsid:marinespecies.org:taxname:164811'
        assert test_row.columns['Kingdom'] == 'Animalia'
        assert test_row.columns['Phylum'] == 'Porifera'
        assert test_row.columns['Class'] == 'Demospongiae'
        assert test_row.columns['Subclass'] == NULL_VAL_STRING
        assert test_row.columns['Order'] == NULL_VAL_STRING
        assert test_row.columns['Suborder'] == NULL_VAL_STRING
        assert test_row.columns['Family'] == NULL_VAL_STRING
        assert test_row.columns['Subfamily'] == NULL_VAL_STRING
        assert test_row.columns['Genus'] == NULL_VAL_STRING
        assert test_row.columns['Subgenus'] == NULL_VAL_STRING
        assert test_row.columns['Species'] == NULL_VAL_STRING
        assert test_row.columns['Subspecies'] == NULL_VAL_STRING
        assert test_row.columns['ScientificNameAuthorship'] == 'Sollas, 1885'
        assert test_row.columns['CombinedNameID'] == 'Demospongiae encrusting'
        assert test_row.columns['Morphospecies'] == 'encrusting'
        assert test_row.columns['Synonyms'] == 'hehe | test'
