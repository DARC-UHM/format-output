"""
Contains functions and constants for printing to terminal.
"""


class Color:
    """
    Some pretty colors.
    """
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
    """
    Messages to print to the terminal.
    """

    LOAD_CONCEPTS_PROMPT = '\nShould the program load previously encountered concept names '\
              'from saved file for a faster runtime?\n\n'\
              f'{Color.GREEN}Y: Use the file {Color.END}(takes < 30 seconds)\n'\
              f'{Color.RED}N: Use WoRMS and overwrite the file {Color.END}(takes 15-20 minutes)\n\n'\
              '>> '

    DIVE_HEADER = f"\n{Color.BOLD}%-35s%-30s%-30s%-s" % ('Dive Name', 'Annotations Found', 'Duplicates Removed', 'Status') + \
        f'\n========================================================================================================={Color.END}'

    WORMS_HEADER = f'\n\n{Color.BOLD}WoRMS check:\n%-40s %-35s%-15s%-15s%-15s%-15s' % \
                   ('VARS Concept Name', 'WoRMS Query', 'Taxon Record', 'Taxon Tree', 'Vernaculars', 'Synonyms (VARS)') + \
                    '\n============================================================================================' + \
                    f'============================================{Color.END}'

    WARNINGS_HEADER = f"\n{Color.BOLD}%-30s%-25s%-40s%-s" % ('Sample ID', 'Concept Name', 'UUID', 'Message') + \
                      '\n============================================================================================' + \
                      f'=========================================================================================={Color.END}'

    @staticmethod
    def dive_not_found(dive_name: str) -> str:
        """
        Returns an error message about missing dive information.

        :param str dive_name: Name of the dive.
        :return str: Error message.
        """
        return(
            f'\n{Color.RED}###################################################################' +
            f'\nERROR: Dive "{dive_name}" not found in Dives.csv file.' +
            '\nThis dive must be added to Dives.csv to continue processing.' +
            f'\n###################################################################\n{Color.END}'
        )
