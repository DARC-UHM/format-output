from typing import Dict

from util.constants import *


class Concept:
    """
    Stores concept information retrieved from WoRMS and the VARS kb.
    """

    def __init__(self, concept_name: str):
        """
        :param str concept_name: The VARS concept name of the organism we want to get information about.
        """
        self.concept_name = concept_name        # the given concept name from the VARS annotation record
        self.aphia_id = NULL_VAL_INT            # to fetch from WoRMS
        self.scientific_name = NULL_VAL_STRING  # to fetch from WoRMS
        self.authorship = NULL_VAL_STRING       # to fetch from WoRMS
        self.vernacular_names = NULL_VAL_STRING # to fetch from WoRMS
        self.synonyms = []                      # to fetch from VARS kb
        self.taxon_rank = NULL_VAL_STRING       # to fetch from WoRMS
        self.taxon_ranks = {}                   # the phylogeny/taxon tree (kingdom, phylum, class, etc)
        self.descriptors = []                   # extra words from the annotation record that aren't the scientific name
        self.concept_words = []                 # for cleaning concept name
        self.concept_add_words = []             # for cleaning concept name
        self.cf_flag = []                       # (cf = compare with) if record includes cf, should be manually reviewed
        self.nr_flag = []                       # (nr = near) should be manually reviewed
        self.aff_flag = []                      # (aff = looks similar to) should be manually reviewed
        self.sp_flag = False                    # used to check whether to append 'sp.' to scientific name

        self.analyze_concept_name()

    def flatten_taxa_tree(self, tree: Dict, flat: Dict):
        """
        Recursive function taking a taxonomy tree returned from WoRMS API. Flattens tree and saves to self.

        :param Dict tree: The nested taxon tree from WoRMS.
        :param Dict flat: The newly created flat taxon tree.
        """
        flat[tree['rank']] = tree['scientificname']
        if tree['child'] is not None:
            self.flatten_taxa_tree(tree['child'], flat)
        elif self.cf_flag:
            ranks = ['Species', 'Genus', 'Family', 'Order', 'Class', 'Phylum']
            for i in range(1, 6):  # from Genus -> Phylum
                if tree['rank'] == ranks[i]:
                    flat[ranks[i - 1]] = f'cf. {" ".join(self.cf_flag)}'  # add 'cf. [concept]' to the rank below

    def load_from_record(self, record: Dict):
        """
        Assigns concept values given JSON object.

        :param Dict record: The JSON object to load data from.
        """
        self.aphia_id = record['AphiaID']
        self.scientific_name = record['scientificname']
        self.taxon_rank = record['rank']
        if self.sp_flag:
            self.scientific_name += ' sp.'
        if self.cf_flag:
            self.scientific_name += ' cf.'
            for name in self.cf_flag:
                self.scientific_name += ' ' + name
        if self.nr_flag:
            self.scientific_name += ' nr.'
            for name in self.nr_flag:
                self.scientific_name += ' ' + name
        if self.aff_flag:
            self.scientific_name += ' aff.'
            for name in self.aff_flag:
                self.scientific_name += ' ' + name
        if record['authority'] is not None:
            self.authorship = record['authority']

    def analyze_concept_name(self):
        """
        Analyzes 'extra bits' (eg 'cf', 'sp', '/') off the VARS concept name:

        EXAMPLE 1:
            VARS concept name = '[genus] [species] cf'
            'cf' means compare with, basically we're sure of the genus but not sure of species... but, it looks "close
            to" this species. We must only report the genus because it's the only thing we're sure of.
            We fetch the genus info from WoRMS and we save [species] and 'cf' locally to add back later.
            The record is populated with the genus info from WoRMS, and the final scientific name reported to DSCRTP is:
            [genus] cf. [species]
            This is the same for aff. (looks similar to) and nr. (near)

        EXAMPLE 2:
            VARS concept name = '[genus] cf sp'
            '[genus] cf' means we're pretty sure it's this genus, but not 100%.
            The 'sp' means it's a species in that genus.
            In this case, we don't care about the 'sp'.
            The record is populated with the FAMILY info from WoRMS (we need to get the genus's parent, then get the
            parent info)
            The final scientific name reported to DSCRTP is: 'cf. [genus]'
        """

        if '/' in self.concept_name:  # account for concepts with slashes in name, e.g. "Ptilella/Pennatula"
            self.descriptors = self.concept_name
            self.concept_words = ['NEED_PARENT']
            return

        self.concept_words = self.concept_name.split(' ')  # create an array of the VARS concept name
        if 'unidentified' in self.concept_words:
            self.concept_words.remove('unidentified')

        # [genus] [species] cf: entity is identified as species within [genus], similar to [species] but not sure
        # [genus] cf: entity is similar to [genus], but not sure
        # can also be [phylum] cf, [class] cf, [subclass] cf, [order] cf, [family] cf
        if 'cf' in self.concept_words:
            if 'sp' in self.concept_words:  # if sp is in this list, just remove it
                del self.concept_words[self.concept_words.index('sp')]
            cf_index = self.concept_words.index('cf')   # get where cf is in the list

            # if cf is the second item in the list, we need to query worms for concept's PARENT
            if cf_index == 1:  # this is the '[genus] cf' case
                del self.concept_words[1]  # remove cf from list
                self.cf_flag = self.concept_words  # we'll use this list to add words back at the very end
                self.concept_words = ['NEED_PARENT']  # get the parent of this concept from HURL later

            else:  # this is the '[genus] [species] cf' case
                # add the word before cf to concept_add_words
                self.concept_add_words.append(self.concept_words[cf_index - 1])
                del self.concept_words[cf_index - 1]  # delete that word from the list
                del self.concept_words[cf_index - 1]  # delete cf from the list
                self.cf_flag = self.concept_add_words

        # [genus] sp: entity is identified as a species within the genus [genus], but the species is unknown
        elif 'sp' in self.concept_words and 'n' not in self.concept_words:
            self.sp_flag = True                             # set this to true so we can add 'sp.' at the end
            sp_index = self.concept_words.index('sp')       # get where sp is in the list
            while sp_index < len(self.concept_words):       # get rid of all list items after sp (including sp)
                if self.concept_words[sp_index] != 'sp':    # append all items except sp to descriptors list
                    self.descriptors.append(self.concept_words[sp_index])
                del self.concept_words[sp_index]

        # [genus] nr [species] &opt[subspecies]: identified as species within [genus], similar to [species] but not sure
        if 'nr' in self.concept_words:
            nr_index = self.concept_words.index('nr')        # get where nr is in the list
            while nr_index < len(self.concept_words):        # get rid of all list items after nr (including nr)
                if self.concept_words[nr_index] != 'nr':     # append all items except nr to nr_flag
                    self.nr_flag.append(self.concept_words[nr_index])
                del self.concept_words[nr_index]

        # [genus] aff [species]: identified as species within [genus], similar to [species] but not sure
        # same as nr
        if 'aff' in self.concept_words:
            aff_index = self.concept_words.index('aff')       # get where aff is in the list
            while aff_index < len(self.concept_words):        # get rid of all list items after aff (including aff)
                if self.concept_words[aff_index] != 'aff':    # append all items except aff to aff_flag
                    self.aff_flag.append(self.concept_words[aff_index])
                del self.concept_words[aff_index]

        # [genus] n sp              -> scientific name: '[genus]', descriptors: 'Undescribed species'
        # [genus] (n subgenus) n sp -> scientific name: '[genus]', descriptors: 'Undescribed subgenus, undescribed species'
        # [family] n gen            -> scientific name: '[family]', descriptors: 'Undescribed genus'
        if 'n' in self.concept_words:
            n_index = self.concept_words.index('n')  # get where n is in the list
            if 'gen' in self.concept_words:
                self.descriptors.append('Undescribed genus')
            elif 'subgenus)' in self.concept_words:
                n_index = self.concept_words.index('(n')  # get where n is in the list
                self.descriptors.append('Undescribed subgenus, undescribed species')
            else:
                self.descriptors.append('Undescribed species')

            while n_index < len(self.concept_words):  # get rid of all list items after n (including n)
                # append all items except n and sp, gen, subgenus to descriptors list
                if self.concept_words[n_index] != 'n' and self.concept_words[n_index] != 'sp' \
                        and self.concept_words[n_index] != 'gen' and self.concept_words[n_index] != 'subgenus)'\
                        and self.concept_words[n_index] != '(n':
                    self.descriptors.append(self.concept_words[n_index])
                del self.concept_words[n_index]
