import csv

# Define the file paths for the two TSV files
test_file = '/Users/darc/Desktop/test.tsv'  # the file we want to test
expected_file = '/Users/darc/Desktop/test1.tsv'  # the file we want to check against

with open(test_file, "r", encoding='ISO-8859-1') as test, open(expected_file, 'r', encoding='ISO-8859-1') as expected:
    test_reader = csv.reader(test, delimiter="\t")
    expected_reader = csv.reader(expected, delimiter="\t")

    # get the header rows for both files
    test_headers = next(test_reader)
    check_headers = next(expected_reader)

    # check if the headers match
    if test_headers != check_headers:
        for i in range(len(test_headers)):
            if test_headers[i] != check_headers[i]:
                print(f'ERROR: Header "{test_headers[i]}" does not match "{check_headers[i]}')
        raise ValueError('The tsv files have different headers')

    # iterate through the rows in the tsv files and compare the values
    different_values = []
    for row_num, (test_row, expected_row) in enumerate(zip(test_reader, expected_reader), start=2):
        # check if the rows have the same number of values
        if len(test_row) != len(expected_row):
            raise ValueError(f'The tsv files have different number of columns at row {row_num}.')

        # compare the values in the rows
        for col_num, (test_val, expected_val) in enumerate(zip(test_row, expected_row), start=1):
            if test_val != expected_val:
                different_values.append((test_val, expected_val, row_num, test_headers[col_num - 1]))

if different_values:
    different_values = sorted(different_values, key=lambda x: x[2])

    columns = {}
    for header in test_headers:
        columns[header] = 0

    print(f'\nThere are a total of {len(different_values)} differences between the two files:\n')

    for test_val, expected_val, row_num, col_name in different_values:
        columns[col_name] += 1

    print("%-40s %-s" % ('Column', 'Num Different Values'))
    print('===============================================================')

    for key, val in columns.items():
        print("%-40s %-4d" % (key, val))

    user_input = ''
    while user_input != 'quit':
        user_input = input('\nEnter a column name to view all of the different values in that column.\n\n'
                           'Enter "cols" to view the columns and values again.\n\n'
                           'Enter "quit" to stop.\n\n'
                           'Input is case sensitive :)\n\n'
                           '>> ')

        if user_input == 'quit':
            break
        elif user_input == 'cols':
            print("%-40s %-s" % ('Column', 'Num Different Values'))
            print('===============================================================')
            for key, val in columns.items():
                print("%-40s %-4d" % (key, val))
        elif user_input in test_headers:
            print('\n')

            # differences = []
            count = 0

            for test_val, expected_val, row_num, col_name in different_values:
                if user_input == col_name:
                    temp_test = test_val.split('; ')
                    temp_expected = expected_val.split('; ')
                    if set(temp_expected) != set(temp_test):
                        print("%-20s %-60s %-60s" % (f'ROW: {row_num}', f'OUTPUT: {test_val}', f'EXPECTED: {expected_val}'))
                        count += 1
                        # differences.append([row_num, test_val, expected_val])

            print(f'\nAdjusted count: {count}\n')
            """ 
            output tsv file of differences for specific columns
            
            with open(f'/Users/darc/Desktop/{user_input}_differences.tsv', 'w', newline='', encoding='utf-8') as file:
                csv_writer = csv.writer(file, delimiter='\t')
                csv_writer.writerow(['Row num', 'Dive', 'UUID', 'Python output', 'Excel output'])
                for message in differences:
                    csv_writer.writerow(message)
            """

            if user_input == 'SampleID':
                print('\n#########################################################################################\n'
                      'NOTE: Excel incorrectly rounds down some instances of 0.5. If the values below are within\n'
                      'one second of each other, it is most likely a rounding error in Excel, not this program.\n'
                      '#########################################################################################\n')
            elif user_input == 'Oxygen':
                print('\n###########################################################################################\n'
                      'NOTE: The values output in the Python script are more precise than the values output by\n'
                      'Excel (the VARS Query used to input vals into Excel rounds the O2 val to 4 decimal places).\n'
                      '###########################################################################################\n')
        else:
            print(f'\nCouldn\'t find column name "{user_input}". Check spelling and case and try again.')

else:
    print('All values in the TSV files are identical.')
