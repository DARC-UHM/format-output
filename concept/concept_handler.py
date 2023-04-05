import sys
import requests

from util.constants import NULL_VAL_STRING
from concept.concept import Concept


class ConceptHandler:
    """ Handles all API requests required to populate Concept fields. Prints status info to terminal. """

    def __init__(self, concept: Concept):
        self.concept = concept                  # concept to update
        self.phylum = ''                        # necessary for confirming correct worms record
        self.found_worms_match = False          # to let user know if matching record has been found
        self.unaccepted_names = []              # keep track of these so we don't add them back at the end

        if 'NEED_PARENT' in concept.concept_words:
            self.find_parent()

    def find_parent(self):
        """
        Gets concept's parent from VARS kb:
        http://hurlstor.soest.hawaii.edu:8083/kb/v1/phylogeny/up/[VARS_CONCEPT_NAME]
        """
        parent = NULL_VAL_STRING
        with requests.get(f'http://hurlstor.soest.hawaii.edu:8083/kb/v1/phylogeny/up/{self.concept.concept_name}') \
                as vars_tax_res:
            if vars_tax_res.status_code == 200:
                # this get us to kingdom
                vars_tree = vars_tax_res.json()['children'][0]['children'][0]['children'][0]['children'][0]
                temp_tree = vars_tree
                while 'children' in vars_tree.keys():
                    # get down to the bottom
                    temp_tree = vars_tree
                    vars_tree = vars_tree['children'][0]
                parent = temp_tree['name']
            else:
                print(f'Unable to find record for {self.concept.concept_name}')
        self.concept.concept_words = [parent]

    def fetch_worms_aphia_record(self):
        """
        Fetches concept info from WoRMS via API call with Scientific name:
        https://www.marinespecies.org/rest/AphiaRecordsByName/[SCIENTIFIC_NAME]?like=true&marine_only=true&offset=1
        """
        # if egg, don't bother checking - will need to add more cases if more egg names are specified in VARS
        if self.concept.concept_name == 'eggs' or self.concept.concept_name == 'eggcase':
            self.concept.scientific_name = 'Animalia'
            self.concept.descriptors = ['egg case'] if self.concept.concept_name == 'eggcase' else [self.concept.concept_name]
            print("%-40s %-35s" % (self.concept.concept_name, 'None'))
            sys.stdout.flush()
            return

        print("%-40s %-35s" % (self.concept.concept_name, " ".join(self.concept.concept_words)), end='')
        sys.stdout.flush()

        with requests.get('https://www.marinespecies.org/rest/AphiaRecordsByName/' +
                          '%20'.join(self.concept.concept_words) + '?like=false&marine_only=true&offset=1') as r:
            if r.status_code == 200:
                json_records = r.json()
                self.find_accepted_record(json_records, self.concept.concept_words)
            else:
                print(f'{"No match" : <15}', end='')
                # Check for extra bits
                for i in range(len(self.concept.concept_words)):
                    if self.concept.concept_words[i] == 'shrimp':
                        self.concept.concept_words[i] = 'Decapoda'
                        self.concept.descriptors.append('shrimp')
                # Then try search WoRMS for each word individually
                for word in self.concept.concept_words:
                    self.concept.concept_add_words.append(word)
                    # skip this query if the name is exactly the same as the first name we used
                    if self.concept.concept_name == ' '.join(self.concept.concept_add_words):
                        break
                    print("\n%-40s %-35s" % ('', " ".join(self.concept.concept_add_words)), end='')
                    sys.stdout.flush()
                    with requests.get('https://www.marinespecies.org/rest/AphiaRecordsByName/' + '%20'.join(
                            self.concept.concept_add_words) + '?like=false&marine_only=true&offset=1') as r2:
                        if r2.status_code == 200:
                            json_records = r2.json()
                            self.find_accepted_record(json_records, self.concept.concept_words)
                        else:
                            print(f'{"No match" : <15}', end='')
                            self.concept.descriptors.append(word)
                            self.concept.concept_add_words.remove(word)
                if len(self.concept.concept_add_words) == 0:
                    # flag error
                    self.concept.concept_name_flag = True

            if self.concept.concept_add_words:
                for word in self.concept.concept_add_words:
                    if word not in self.concept.scientific_name and word not in self.unaccepted_names:
                        self.concept.descriptors.append(word)

    def find_accepted_record(self, json_records, concept_words):
        """
        Finds matching record in API query from WoRMS:
        http://hurlstor.soest.hawaii.edu:8083/kb/v1/phylogeny/up/[VARS_CONCEPT_NAME]

        Problem: There are multiple concepts with the same scientific name.
            e.g. Stolonifera: there is one concept named Stolonifera in phylum Bryozoa and another concept named
            Stolonifera in phylum Cnidaria. We want the one from Cnidaria, but its status is unaccepted (so we can't
            simply check the concept's status in the response JSON and use that concept).

        Solution: If there is more than one object in the response body, get the concept's phylum by doing a VARS API
            query with the concept name. Use the object in the response whose phylum matches the VARS phylum. If there
            is more than one match, go with the match that is accepted.
        """
        if len(json_records) == 1:
            # there is only one record, use it
            self.check_status(json_records[0])
        else:
            # there are multiple records - we need to ping vars for phylum and find the record that matches
            with requests.get(f'http://hurlstor.soest.hawaii.edu:8083/kb/v1/phylogeny/up/{"%20".join(concept_words)}') \
                    as vars_tax_res:
                if vars_tax_res.status_code == 200:
                    # this get us to kingdom
                    vars_tree = vars_tax_res.json()['children'][0]['children'][0]['children'][0]['children'][0]
                    while not self.phylum:
                        # find the phylum in the response tree
                        vars_tree = vars_tree['children'][0]
                        if 'rank' in vars_tree.keys() and vars_tree['rank'] == 'phylum':
                            self.phylum = vars_tree['name']

            record_list = []
            for record in json_records:
                # get record with matching phylum
                if record['phylum'] == self.phylum:
                    record_list.append(record)

            for i in range(len(record_list)):
                # look for accepted record in matching phylum list
                if record_list[i]['status'] == 'accepted':
                    self.check_status(record_list[i])
                    del record_list[i]
                    break

            if not self.found_worms_match:
                if record_list:
                    self.check_status(record_list[0])
                else:
                    print('No match')
                    self.concept.concept_name_flag = True

    def check_status(self, json_record):
        """
        Checks a record to see if it has a status of 'accepted'. If it does, it uses that record to load concept info.
        If it doesn't, it fetches the 'valid name' record that the unaccepted record points to.
        """
        if json_record['status'] == 'accepted':
            print(f'{" ✓" : <15}', end='')
            sys.stdout.flush()
            self.found_worms_match = True
            self.concept.load_from_record(json_record)
        else:
            print('Unaccepted')
            self.unaccepted_names.append(json_record['scientificname'])
            print("%-40s %-35s" % ('', json_record['valid_name']), end='')
            sys.stdout.flush()
            with requests.get('https://www.marinespecies.org/rest/AphiaRecordsByName/' + json_record['valid_name'] +
                              '?like=false&marine_only=true&offset=1') as r:
                if r.status_code == 200:
                    json_records = r.json()
                    self.find_accepted_record(json_records, json_record['valid_name'])

    def fetch_worms_taxon_tree(self):
        """
        Pulls taxon tree info from WoRMS:
        https://www.marinespecies.org/rest/AphiaClassificationByAphiaID/[APHIA_ID]
        """
        if self.concept.concept_name == 'eggs' or self.concept.concept_name == 'eggcase':
            self.concept.taxon_ranks = {'Kingdom': 'Animalia'}
            return

        if self.concept.scientific_name != NULL_VAL_STRING:
            with requests.get(
                    'https://www.marinespecies.org/rest/AphiaClassificationByAphiaID/' + str(self.concept.aphia_id)) as r:
                if r.status_code == 200:
                    taxon_tree = r.json()
                    self.concept.flatten_taxa_tree(taxon_tree, self.concept.taxon_ranks)
                    print(f'{" ✓" : <15}', end='')
                    sys.stdout.flush()
                else:
                    print(f'{"No match" : <15}')

    def fetch_vernaculars(self):
        """
        Fetches all english vernacular names for a given aphia ID from WoRMS:
        https://www.marinespecies.org/rest/AphiaVernacularsByAphiaID/[APHIA_ID]
        """
        if self.concept.concept_name == 'eggs' or self.concept.concept_name == 'eggcase':
            return
        vern_names = NULL_VAL_STRING
        with requests.get(
                'https://www.marinespecies.org/rest/AphiaVernacularsByAphiaID/' + str(self.concept.aphia_id)) as r:
            if r.status_code == 200:
                for record in r.json():
                    if record['language_code'] == 'eng':
                        if vern_names != NULL_VAL_STRING:
                            vern_names = f'{vern_names} | {record["vernacular"]}'
                        else:
                            vern_names = record["vernacular"]
                print(f'{" ✓" : <15}', end='')
                sys.stdout.flush()
            else:
                print(f'{"None found" : <15}', end='')

        self.concept.vernacular_names = vern_names

    def fetch_vars_synonyms(self):
        """
        Fetches synonym info from VARS kb:
        http://hurlstor.soest.hawaii.edu:8083/kb/v1/concept/[VARS_CONCEPT_NAME]
        """
        if self.concept.concept_name == 'eggs' or self.concept.concept_name == 'eggcase':
            return
        url = f'http://hurlstor.soest.hawaii.edu:8083/kb/v1/concept/{self.concept.concept_name.replace(" ", "%20")}'
        nicknames = []
        with requests.get(url) as r:
            json_obj = r.json()
            if r.status_code == 200:
                for syn in json_obj['alternateNames']:
                    # names starting with a lowercase letter are common names, not of interest
                    if syn[0].isupper():
                        nicknames.append(syn)
                print(' ✓') if nicknames else print('None found')
                self.concept.synonyms = nicknames
