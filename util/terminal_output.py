""" Contains functions for printing to terminal """


class Color:
    """ Some pretty colors """
    PURPLE = '\033[1;35;48m'
    CYAN = '\033[1;36;48m'
    BOLD = '\033[1m'
    BLUE = '\033[1;34;48m'
    GREEN = '\033[1;32;48m'
    YELLOW = '\033[1;33;48m'
    RED = '\033[1;31;48m'
    BLACK = '\033[1;30;48m'
    UNDERLINE = '\033[4;37;48m'
    END = '\033[1;37;0m'


class Messages:

    @staticmethod
    def dive_not_found(dive_name):
        print(f'\n{Color.RED}###################################################################')
        print(f'ERROR: Dive "{dive_name}" not found in Dives.csv file.')
        print('This dive must be added to Dives.csv to continue processing.')
        print(f'###################################################################\n{Color.END}')

    @staticmethod
    def dive_header():
        print(f"\n{Color.BOLD}%-35s%-30s%-30s%-s" % ('Dive Name', 'Annotations Found', 'Duplicates Removed', 'Status'))
        print('============================================================================================'
              f'============={Color.END}')

    @staticmethod
    def worms_header():
        print(f'\n\n{Color.BOLD}WoRMS check:')
        print("\n%-40s %-35s%-15s%-15s%-15s%-15s" %
              ('VARS Concept Name', 'WoRMS Query', 'Taxon Record', 'Taxon Tree', 'Vernaculars',
               'Synonyms (VARS)'))
        print('============================================================================================'
              f'============================================{Color.END}')

    @staticmethod
    def warning_header():
        print(f"\n{Color.BOLD}%-30s%-25s%-40s%-s" % ('Sample ID', 'Concept Name', 'UUID', 'Message'))
        print('============================================================================================'
              f'=========================================================================================={Color.END}')
