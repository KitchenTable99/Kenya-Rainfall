# This file will perform the necessary hazard regressions
# Caleb Bitting (Colby Class of 2023)
# Written for research for Professor Daniel LaFave at Colby College
#

import argparse
import pandas as pd
from lifelines import CoxPHFitter

def commandLineParser():
    '''This function parses the command line arguments
    
    Returns:
        argparse.namespace: an argparse namespace representing the command line arguments
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('rainfall_data', type=str, help='the path to the csv containing the rainfall data.')
    parser.add_argument('DHS_data', type=str, help='the path to the csv containing the DHS survey data.')
    args = parser.parse_args()

    return args

def main():
    # get command line arguments
    cmd_args = commandLineParser()
    # import data (mother/rain)
    rainfall_df = pd.read_csv(cmd_args.rainfall_data)
    mother_df = pd.read_csv(cmd_args.DHS_data)
    # get relevant data from rain data
    merged = pd.merge(mother_df, rainfall_df, on=['DHSID', 'Year'], how='left')
    merged.set_index('IDHSPID', inplace=True)
    # drop unneeded columns
    drop_columns = ['DHSID', 'Year', r'%-ile', 'Total Rainfall (mm)']
    for column in merged.columns:
        if column in drop_columns:
            merged.drop(column, axis=1, inplace=True)
    # change Bools into ones or zeros
    for column in [r'<5%-ile', r'<10%-ile', r'<15%-ile']:
        merged[column] = (merged[column] == True).astype(int)
    # regressions
    cph = CoxPHFitter()
    cph.fit(merged, 'Event Time', event_col='Event Occured')
    # display results
    cph.print_summary()

if __name__ == '__main__':
    main()