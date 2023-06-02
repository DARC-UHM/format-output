[![Build Status](https://github.com/DARC-UHM/Format-Output/actions/workflows/python-app.yml/badge.svg)](https://github.com/DARC-UHM/Format-Output/actions/workflows/python-app.yml)

### Overview

This program compiles annotation data for a specified list of dives and outputs a .tsv file with formatted data for insertion into the DSCRTP database. An example of the expected output can be found in this directory (Expected Output.txt). This is a tsv file with a .txt extension.

The program gathers data from four sources:
- **HURLSTOR**: The majority of the data is gathered by directly accessing the VARS database on HURLSTOR. Fields specific to each record are filled out from the fields in VARS.
- **WoRMS**: Taxonomic data for animals is gathered by accessing the WoRMS database. The script automatically formats VARS concept names into scientific names that get a response from WoRMS. 
- **Dives.csv**: Any empty fields in this file will result in the corresponding field in the output file to be set to "NA". This file:
  - Contains a list of every dive along with some administrative information about each dive
  - Must be located in the same directory from which the user calls the script
  - Must have information about all of the dives that are to be processed
  - Is maintained manually
- **A list of video sequence names**: This is a file detailing which video sequence names to access in the HURL database. The path to this file is manually provided while running the script.

### Usage

_Requires Python ≥ 3.9_

1. Clone this repository.
2. Run `pip3 install -r requirements.txt`.
3. From the base directory run `python3 format_and_worms.py` Note: the script must be run from the same directory that contains `references/Dives.csv`.
4. The script will prompt `Should the program load previously encountered concept names from a saved file for a faster runtime?
(Y: Use the file; N: Use WoRMS and overwrite the file)`. If this is your first time running the script, no matter what you enter here, the script will use WoRMS to download current taxa information. This will take about 20 minutes, depending on the number of records to be processed. If you have run the script before, you can enter `y` to skip this process.
5. The script will then prompt `Name of output file (without the .tsv file extension):`. Enter any name.
6. The next prompt is `Path to folder of output files:`. Enter the path you want the formatted output files to be saved. Note: Using `~/` does not work on MacOS, use `/Users/[username]/` instead.
7. The final prompt is `Path to a list of sequence names:`. Enter the path to the list of dive sequences you want to process. You can use the example file in this repository `references/test_sequences.csv` or use your own list of sequence names.
8. The script will run and output the formatted data as a tsv file.

Notes: 
- Does not support the Linux file structure.
- CTD and Nav data must be merged and linked before this script is run. This must be done locally at DARC by running the script `darc_merge_nav_ctd`

### Modifications and Updates

**Adding columns**: To add a new column to the output file, some modifications must be made to the source code:

1. In `util/constants.py`, add the new column name to the desired location in the `HEADERS` variable. Adjust the number comments to the right of each column name to reflect the newly inserted column. 
2. In the same file, adjust the column number variables above the `HEADERS` variable to reflect the shifted column numbers.
3. In `format_output.py`, increment the number in the two `csv_writer.writerow` lines (lines 281 and 283).

At this point, the output file should contain the newly added column in the correct place, with each field populated with `NA`. To populate the field with the correct data, modifications must be made to `format_and_output.py` and/or `annotation/annotation_row.py`.

_For columns with simple data that come directly from the VARS database with little or no modification:_ 

1. Go to the `set_simple_static_data` function declaration in `annotation/annotation_row.py` (line 30).
2. Anywhere inside the function, add a line that sets the value of the new column to the data from the JSON object received from VARS.

Example: We have added a column named `VideoTrackingID` that should contain the `video_reference_uuid` for each record. In the `set_simple_static_data` function, we can simply add the line 
```python
self.columns['VideoTrackingID'] = self.annotation['video_reference_uuid']
```
anywhere inside the function. The output file will now populate the field with the correct value.

_For more columns with more complicated data that requires modification after receipt from VARS:_

1. Create a new function in `annotation/annotation_row.py` that contains the logic to manipulate the data before adding it to the output file.
2. Add a call to this function in `format_and_output.py` somewhere around line 240.

Example: We have added a column named `TimeElapsed` that should contain the time elapsed since the start of the video, formatted as HH:MM:SS. In `annotation/annotation_row.py`, we declare a new function

```python
def set_time_elapsed(self):
    time_elapsed_millis = self.annotation['elapsed_time_millis']
    seconds = round(time_elapsed_millis / 1000 % 60)
    minutes = math.floor(time_elapsed_millis / 60000 % 3600000 % 60)
    hours = math.floor(time_elapsed_millis / 3600000)
    formatted_time = '%02d:%02d:%02d' % (hours, minutes, seconds)
    self.columns['TimeElapsed'] = formatted_time
```

And in `format_output.py`, we make call to the function

```python
...
240    annotation_row.set_time_elapsed()
...
```

The output file will now populate the field with the correct value.

_Note_: adding a column will break some of the unit tests - specifically the last 10 or so in `test/test_functions.py`. You can either add the new column to the test data (`sample_report_records`, `sample_report_records_collapsed`, and `sample_report_records_collapsed` in `test/data_for_tests.py`) or you can ignore these errors.