# This script will create the rainfall data needed to analyze the economc shocks in Keyna
# Created by Caleb Bitting (Colby class of 2023)
#

import os
import argparse
import file_parsers as fp
from tqdm import tqdm as progress

def importPrecipData(month_range, precip_data_folder='./resources/precip_data', sum_data=True, testing=False):
    '''This function imports all precip data in ./resources/precip_data or another specified folder
    
    Args:
        month_range (list): a list of months across which to sum the rainfall
        precip_data_folder (str, optional): a string representing the path to the folder in which all of the .precip files are stored. Defaults to './resources/precip_data'
        sum_data (bool, optional): whether or not to sum the rainfall data across the selected months. Defaults to True
        testing (bool, optional): wheter or not the function is in testing mode. If so, only the first ten precip files will be considered for speed. Defaults to False
    
    Returns:
        list: a list of parsed precip data. Of the form [[[x1, y1], SUM2], [[x2, y2], SUM2], ...] where SUM is the sum of the rainfall in the selected months
    '''
    # get list of precip files
    os.system(f'cd {precip_data_folder}; ls precip* > ../../precip.txt')
    with open('precip.txt', 'r') as f:
        precip_contents = f.read()
    precip_contents = precip_contents.split('\n')
    precip_contents.pop()
    if testing:
        precip_contents = precip_contents[:10]      # only take the first ten items if testing is passed as True
    os.system('rm precip.txt')
    # modify the path variable
    precip_contents = ['./resources/precip_data/' + file for file in precip_contents]
    # create precip data list for them all
    precip_data = [fp.precipFileParser(path, month_range, sum_data) for path in progress(precip_contents, desc='Importing precip data')]

    return precip_data

def commandLineParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('unit_code', type=int, help='the unit code that designates the area of interest. See ./resources/unit_name.txt for list of unit codes.')
    args = parser.parse_args()

    return args

def test():
    cmd_args = commandLineParser()
    # month_range = fp.cropCalendarParser(cmd_args.unit_code)
    # month_range = [int(month) for month in month_range]
    # test = importPrecipData(month_range, testing=True)
    # print(test[0])
    st_coords = fp.precipFileParser('./resources/precip_data/precip.1977', [4, 8], return_coords=True)
    gdf = fp.shapeFileParser('./resources/kenya_dhs_2013/KEGE43FL.shp', st_coords)

if __name__ == '__main__':
    test()
