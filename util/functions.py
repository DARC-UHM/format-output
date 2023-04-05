"""
This file contains functions that are used throughout the formatting process and WoRMS check.
"""

from datetime import datetime, timedelta

from concept.concept import Concept
from concept.concept_handler import ConceptHandler
from util.constants import *


def get_association(annotation, link_name):
    """ Obtains an association value from the annotation data structure """
    for association in annotation['associations']:
        if association['link_name'] == link_name:
            return association
    return None


def get_associations_list(annotation, link_name):
    """ Obtains a list association values from the annotation data structure """
    association_matches = []
    for association in annotation['associations']:
        if association['link_name'] == link_name:
            association_matches.append(association)
    return association_matches


def grain_size(sub):
    """ Gets the relative grain size of a substrate concept """
    for i in range(len(ROOTS)):
        if ROOTS[i] in sub:
            return i
    return len(ROOTS)


def get_date_and_time(record):
    """ Returns a datetime timestamp from a record """
    return datetime.strptime(record[OBSERVATION_DATE] + record[OBSERVATION_TIME], '%Y-%m-%d%H:%M:%S')


def parse_datetime(timestamp):
    """ Returns a datetime object given a timestamp string """
    if '.' in timestamp:
        return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
    return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')


def extract_time(json_object):
    """ For sorting json object by timestamp given a json object """
    if '.' in json_object['recorded_timestamp']:
        timestamp = datetime.strptime(json_object['recorded_timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if timestamp.microsecond >= 500000:
            return timestamp.replace(microsecond=0) + timedelta(seconds=1)
        return timestamp.replace(microsecond=0)
    return datetime.strptime(json_object['recorded_timestamp'], '%Y-%m-%dT%H:%M:%SZ')


def extract_uuid(json_object):
    """ For sorting annotations by UUID so we can check final output against expected
    (the expected out put is sorted by uuid, then by time) """
    return json_object['observation_uuid']


def add_meters(accuracy):
    """ Takes input and appends an 'm' to the end if one is not there already """
    if accuracy[-1:] != 'm':
        accuracy = accuracy + 'm'
    return accuracy


def convert_username_to_name(vars_username):
    """ Converts VARS username to proper format: [FirstnameLastName] -> [Lastname, FirstName] """
    for i in range(1, len(vars_username)):
        if vars_username[i].isupper():
            return vars_username[i:] + ', ' + vars_username[0:i]
    return vars_username


def translate_substrate_code(code):
    """ Translates substrate codes into human language """
    if code in SAMES:
        return code
    substrate_word_list = []
    r = ''
    man_or_forms = []
    for root in ROOTS:
        if root in code:
            substrate_word_list.append(SUB_CONCEPTS[root])
            r = SUB_CONCEPTS[root]
            code = code.replace(root, '')
            if code == '':
                if r == 'man-made':
                    return 'man-made object'
                else:
                    return r
            break
    for affix in ALL_AFFIXES:
        if affix in code:
            if affix == 'pi':
                if r == 'bedrock' or r == 'block':
                    substrate_word_list.insert(0, SUB_CONCEPTS[affix][0])
                else:
                    substrate_word_list.append(SUB_CONCEPTS[affix][1])
            elif affix in SUFFIXES and r in substrate_word_list:
                substrate_word_list.insert(substrate_word_list.index(r) + 1, SUB_CONCEPTS[affix])
            elif affix in SUFFIXES_FORMS or affix in SUFFIXES_MAN:
                substrate_word_list.append(SUB_CONCEPTS[affix])
                man_or_forms.append(affix)
            elif affix in SUFFIXES_DEAD:
                substrate_word_list.append(SUB_CONCEPTS[affix])
            elif affix in PREFIXES and r in substrate_word_list:
                substrate_word_list.insert(substrate_word_list.index(r), SUB_CONCEPTS[affix])
            code = code.replace(affix, '')
            if code == '':
                if len(man_or_forms) >= 2:
                    substrate_word_list.insert(-1, 'and')
                subs = ' '.join(substrate_word_list)
                if subs[:4] == 'dead':
                    subs = f'{subs[5:]} (dead)'
                return subs
    return ''

