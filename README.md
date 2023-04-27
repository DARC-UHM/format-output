[![Build Status](https://github.com/DARC-UHM/Format-Output/actions/workflows/python-app.yml/badge.svg)](https://github.com/DARC-UHM/Format-Output/actions/workflows/python-app.yml)

### Overview

This program compiles annotation data for a specified list of dives and outputs a .tsv file with formatted data for insertion into the DSCRTP database. An example of the expected output can be found in this directory (Expected Output.txt). This is a tsv file with a .txt extension.

The program gathers data from four sources:
- **HURL**: The majority of the data is gathered by directly accessing the online HURL database. Fields specific to each record are filled out from the fields in VARS.
- **WoRMS**: Taxonomic data for animals is gathered by accessing the WoRMS database online. The script automatically formats VARS concept names into scientific names that get a response from WoRMS. 
- **Dives.csv**: Any fields left empty will be left as “NA” in the output. This file:
  - Contains a list of every dive along with some administrative information about each dive
  - Must be in the same directory that user calls the script
  - Must have information about all of the dives that are to be processed
  - Is maintained manually
- **A list of video sequence names**: This is a file detailing which video sequence names to access in the HURL database. The path to this file is manually provided while running the script.

### Usage

1. Clone this repository.
2. Install Python 3.
3. Run `pip3 install -r requ`.
4. From the base directory run `python3 format_and_worms.py` Note: the script must be run from the same directory that contains `references/Dives.csv`.
5. The script will prompt `Should the program load previously encountered concept names from a saved file for a faster runtime?
(Y: Use the file; N: Use WoRMS and overwrite the file)`. If this is your first time running the script, no matter what you enter here, the script will use WoRMS to download current taxa information. This will take about 20 minutes. If you have run the script before, you can enter `y` to skip this process.
6. The script will then prompt `Name of output file (without the .tsv file extension):`. Enter any name.
7. The next prompt is `Path to folder of output files:`. Enter the path you want the formatted output files to be saved. Note: Using `~/` does not work on MacOS, use `/Users/[username]/` instead.
8. The final prompt is `Path to a list of sequence names:`. Enter the path to the list of dive sequences you want to process. You can use the example file in this repository `references/test_sequences.csv` or use your own list of sequence names.
9. The script will run and output two files: the formatted data, and a list of messages with records that should be reviewed.

Notes: 
- Does not support the Linux file structure.
- CTD and Nav data must be merged and linked before this script is run. This must be done locally at DARC by running a script called `darc_merge_nav_ctd`
