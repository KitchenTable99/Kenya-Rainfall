# This script will create the rainfall data needed to analyze the economc shocks in Keyna
# Caleb Bitting (Colby Class of 2023)
# Written for research for Professor Daniel LaFave at Colby College
#

import os
import pickle
import argparse
import itertools
import statistics
import file_parsers as fp
from termcolor import cprint
from tqdm import tqdm as progress

def importPrecipData(month_range, windows='', precip_data_folder='./resources/precip_data', testing=False):
    '''This function imports all precip data in ./resources/precip_data or another specified folder
    
    Args:
        month_range (list): a list of months across which to sum the rainfall
        windows (str, optional): a string representing the path to the file containing the names of the precip files. Defaults to the empty string.
        precip_data_folder (str, optional): a string representing the path to the folder in which all of the .precip files are stored. Defaults to './resources/precip_data'
        testing (bool, optional): wheter or not the function is in testing mode. If so, only the first ten precip files will be considered for speed. Defaults to False
    
    Returns:
        list: a list of parsed precip data. Of the form [[[x1, y1], SUM2], [[x2, y2], SUM2], ...] where SUM is the sum of the rainfall in the selected months
    '''
    # get list of precip files
    if windows:
        precip_contents = fp.precipListParser(windows, testing=testing)
    else:
        os.system(f'cd {precip_data_folder}; ls precip* > ../../precip.txt')
        precip_contents = fp.precipListParser('precip.txt', testing=testing)
        os.system('rm precip.txt')
    # modify the path variable
    precip_contents = ['./resources/precip_data/' + file for file in precip_contents]
    # create precip data list for them all
    precip_data = [fp.precipFileParser(path, month_range) for path in progress(precip_contents, desc='Importing precip data')]

    return precip_data

def commandLineParser():
    '''This function parses the command line arguments
    
    Returns:
        argparse.namespace: an argparse namespace representing the command line arguments
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--unit_code', required=True, type=int, help='the unit code that designates the area of interest. See ./resources/unit_name.txt for list of unit codes.')
    parser.add_argument('--distance', required=True, type=float, default=10., help='the maximum distance (in km) allowed between a DHS center and a precip grid center. Defaults to 10.0 km.')
    parser.add_argument('--shapefile_path', required=True, type=str, help='the path to the .shp file in a shapefile folder. This folder should be expanded from a .zip file.')
    parser.add_argument('--csv_name', type=str, default='data.csv', help='the name of the csv to which this program will write. Defaults to data.csv')
    parser.add_argument('--testing', action='store_true', help='enter testing mode. All functions will be passed testing=True where possible.')
    parser.add_argument('--windows', '-w', type=str, help='the file path for the list of the names of precip files.')
    parser.add_argument('--determine_distance', default=False, help='needed for file_parsers. DO NOT TOUCH.')
    args = parser.parse_args()

    return args

def generateRainFallSums(index_list, precip_data):
    '''This function generates all rainfall sums for a particular location.
    
    Args:
        index_list (list): all of the relevant indices. 'Station Indices' column in GeoDataFrame.
        precip_data (list): 2-D list of all rainfall data. Returned by fp.precipFileParser()
    
    Returns:
        list: the sums for every rainfall year of the relevant stations. Of the form [sum1, sum2, sum3, ...]
    '''
    rainfall_totals = [sum([item for index, item in enumerate(lst) if index in index_list]) for lst in precip_data]
    return rainfall_totals

def body(cmd_args):
    '''This function runs the main functionality
    
    Args:
        cmd_args (argparse.Namespace): an argparse namespace
    
    Returns:
        GeoDataFrame: a GeoPandas GeoDataFrame with all of the rainfall sums included.
    '''
    '''
    # parse month range
    month_range = fp.cropCalendarParser(cmd_args.unit_code)
    month_range = [int(month) for month in month_range]
    # get precip data
    precip_data = importPrecipData(month_range, windows=cmd_args.windows, testing=cmd_args.testing)
    '''
    with open('full_precip.pickle', 'rb') as f:
        precip_data = pickle.load(f)
    # get geodata
    st_coords = fp.precipFileParser('./resources/precip_data/precip.1977', [4, 8], return_coords=True)
    gdf = fp.shapeFileParser(cmd_args.shapefile_path, st_coords, cmd_args, testing=cmd_args.testing)
    # generate rainfall totals
    station_indices = gdf['Station Indices'].tolist()
    rainfall_totals = [generateRainFallSums(index_list, data) for index_list, data in progress(zip(station_indices, itertools.repeat(precip_data)), total=len(gdf['Station Indices']), desc='Calculating rainfall sums')]
    gdf['Rainfall Totals'] = rainfall_totals
    # print out needed calculation stats
    station_lengths = [len(lst) for lst in station_indices]     # how many stations were captured
    _, columns = os.popen('stty size', 'r').read().split()
    fancy_sep = ['-' for _ in range(int(columns))]
    print(''.join(fancy_sep))                                   # allow for some eyeball breathing room
    print(f'The average number of captured stations was {round(statistics.mean(station_lengths), 2)}')
    if 0 in station_lengths:                                    # warn if any location didn't capture data
        cprint('::ATTENTION::', 'red', attrs=['reverse', 'blink'])
        print(f'{station_lengths.count(0)}/{len(station_lengths)} locations did not capture a single precip station. This will *likely* be addressed in the final csv file.')
    else: print('Every location captured at least one precip station.')

    return gdf

def main():
    # get command line arguments
    cmd_args = commandLineParser()
    # call functionality
    gdf = body(cmd_args)
    # store in csv
    if '.csv' not in cmd_args.csv_name: cmd_args.csv_name += '.csv'
    gdf.to_csv(cmd_args.csv_name, index=False)

if __name__ == '__main__':
    main()
