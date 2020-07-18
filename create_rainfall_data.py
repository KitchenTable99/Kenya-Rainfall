# This file will run all the scripts needed to create a finalied .csv file containing %-ile rainfall data 
# Caleb Bitting (Colby Class of 2023)
# Written for research for Professor Daniel LaFave at Colby College
#

import os
import argparse
import csv_polishing
import rainfall_sums
import gamma_calculations

def commandLineParser():
    '''This function parses the command line arguments
    
    Returns:
        argparse.namespace: an argparse namespace representing the command line arguments
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('unit_code', type=int, help='the unit code that designates the area of interest. See ./resources/unit_name.txt for list of unit codes.')
    parser.add_argument('len_years', type=int, help='the number of years to use to fit each gamma distribution.')
    parser.add_argument('--csv_name', '-n', type=str, default='data.csv', help='the name of the csv to which this program will write. Defaults to data.csv')
    parser.add_argument('--testing', '-t', action='store_true', help='enter testing mode. All functions will be passed testing=True where possible.')
    parser.add_argument('--station_dist', '-d', type=float, default=10., help='the maximum distance (in km) allowed between a DHS center and a precip grid center. Defaults to 10.0 km.')
    parser.add_argument('--windows', '-w', type=str, help='the file path for the list of the names of precip files.')
    parser.add_argument('--verbose', '-v', action='store_true', help='whether or not to see the intermediate progress bar')
    parser.add_argument('--first_year', type=int, default=1980, help='the year corresponding to the first value of the precipitation percentile. Output by gamma_calculations.py. Defaults to 1980')
    parser.add_argument('--output_file', type=str, default='cleanGamma_data.csv', help='the name of the processed csv. Defaults to cleanGamma_data.csv')
    args = parser.parse_args()

    return args

def main():
    # command-line arguments
    cmd_args = commandLineParser()
    # get rainfall sums
    gdf = rainfall_sums.body(cmd_args)
    # eye breathing room
    _, columns = os.popen('stty size', 'r').read().split()
    fancy_sep = ['-' for _ in range(int(columns))]
    print(''.join(fancy_sep)) 
    # get percentile data
    rainfall_list = gdf['Rainfall Totals'].tolist()
    percentiles = gamma_calculations.body(rainfall_list, cmd_args)
    # edit csv
    df = csv_polishing.body(rainfall_list, percentiles, cmd_args)
    df.to_csv('end.csv', index=False)


    

if __name__ == '__main__':
    main()