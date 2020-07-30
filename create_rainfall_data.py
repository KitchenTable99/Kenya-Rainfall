# This file will run all the scripts needed to create a finalied .csv file containing %-ile rainfall data 
# Caleb Bitting (Colby Class of 2023)
# Written for research for Professor Daniel LaFave at Colby College
#

import os
import argparse
import itertools
import numpy as np
import pandas as pd
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
    parser.add_argument('--len_years', default=30, type=int, help='the number of years to use to fit each gamma distribution. Defaults to 30')
    parser.add_argument('--output_file', type=str, default='cleanGamma_data.csv', help='the name of the processed csv. Defaults to cleanGamma_data.csv')
    parser.add_argument('--windows', '-w', type=str, help='the file path for the list of the names of precip files.')
    parser.add_argument('--verbose', '-v', action='store_true', help='whether or not to see the intermediate progress bar')
    parser.add_argument('--testing', '-t', action='store_true', help='enter testing mode. All functions will be passed testing=True where possible.')
    parser.add_argument('--determine_distance', default=False, help='needed for file_parsers. DO NOT TOUCH.')
    args = parser.parse_args()

    return args

def getNum(biggest):
    usr_inp = input('Shapefile number:  ')
    if int(usr_inp) > biggest:
        print('\nNot a valid number.')
        getNum(biggest)

    return int(usr_inp)

def printClearLine():
    _, columns = os.popen('stty size', 'r').read().split()
    fancy_sep = ['-' for _ in range(int(columns))]
    print(''.join(fancy_sep)) 

def main():
    # command-line arguments
    cmd_args = commandLineParser()
    # find shapefiles recursively
    shapefiles = []
    shapefile_paths = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.shp'):
                shapefiles.append(file)
                shapefile_paths.append(os.path.join(root, file))
    if len(shapefiles) == 0:
        raise Exception('No shapefiles were found.')
    else:
        printClearLine()
        print('Which shapefile would you like to use?')
        for index, shapefile in enumerate(shapefiles):
            print(f'[{index+1}]\t{shapefile}')
    usr_shp_file = getNum(len(shapefiles))
    cmd_args.shapefile_path = shapefile_paths[usr_shp_file - 1]
    # get rainfall sums
    gdf = rainfall_sums.body(cmd_args)
    # eye breathing room
    printClearLine()
    # get percentile data
    rainfall_list = gdf['Rainfall Totals'].tolist()
    percentiles = gamma_calculations.body(rainfall_list, cmd_args)
    # edit csv
    year = 1950 + cmd_args.len_years
    df = csv_polishing.body(rainfall_list, percentiles, year)
    # get DHSID
    DHSID_col = gdf['DHSID'].repeat(len(percentiles[0]))
    DHSID_col = DHSID_col.reset_index(drop=True)
    df.insert(0, 'DHSID', DHSID_col, allow_duplicates=True)
    df.drop('Location', axis=1, inplace=True)
    # output
    df.to_csv(cmd_args.output_file, index=False)

if __name__ == '__main__':
    main()