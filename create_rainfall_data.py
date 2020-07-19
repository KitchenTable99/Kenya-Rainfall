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
    parser.add_argument('--unit_code', required=True, type=int, help='the unit code that designates the area of interest. See ./resources/unit_name.txt for list of unit codes.')
    parser.add_argument('--distance', required=True, type=float, default=10., help='the maximum distance (in km) allowed between a DHS center and a precip grid center.')
    parser.add_argument('--shapefile_path', required=True, type=str, help='the path to the .shp file in a shapefile folder. This folder should be expanded from a .zip file.')
    parser.add_argument('--len_years', required=True, type=int, help='the number of years to use to fit each gamma distribution.')
    parser.add_argument('--output_file', type=str, default='cleanGamma_data.csv', help='the name of the processed csv. Defaults to cleanGamma_data.csv')
    parser.add_argument('--windows', '-w', type=str, help='the file path for the list of the names of precip files.')
    parser.add_argument('--verbose', '-v', action='store_true', help='whether or not to see the intermediate progress bar')
    parser.add_argument('--testing', '-t', action='store_true', help='enter testing mode. All functions will be passed testing=True where possible.')
    parser.add_argument('--determine_distance', default=False, help='needed for file_parsers. DO NOT TOUCH.')
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
    year = 1950 + cmd_args.len_years
    df = csv_polishing.body(rainfall_list, percentiles, year)
    df.to_csv(cmd_args.output_file, index=False)


    

if __name__ == '__main__':
    main()