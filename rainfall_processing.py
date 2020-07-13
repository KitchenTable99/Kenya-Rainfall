# This script will create the rainfall data needed to analyze the economc shocks in Keyna
# Created by Caleb Bitting (Colby class of 2023)
#

import os
import file_parsers as fp
from tqdm import tqdm as progress

def importPrecipData(month_range, precip_data_folder='./resources/precip_data', sum_data=True):
    '''This function imports all precip data in ./resources/precip_data or another specified folder
    
    Args:
        month_range (list): a list of months across which to sum the rainfall
        precip_data_folder (str, optional): a string representing the path to the folder in which all of the .precip files are stored. Defaults to './resources/precip_data'
        sum_data (bool, optional): whether or not to sum the rainfall data across the selected months. Defaults to True
    
    Returns:
        list: a list of parsed precip data. Of the form [[[x1, y1], SUM2], [[x2, y2], SUM2], ...] where SUM is the sum of the rainfall in the selected months
    '''
    # get list of precip files
    os.system(f'cd {precip_data_folder}; ls precip* > ../../precip.txt')
    with open('precip.txt', 'r') as f:
        precip_contents = f.read()
    precip_contents = precip_contents.split('\n')
    precip_contents.pop()
    os.system('rm precip.txt')
    # modify the path variable
    precip_contents = ['./resources/precip_data/' + file for file in precip_contents]
    # create precip data list for them all
    precip_data = [fp.precipFileParser(path, month_range, sum_data) for path in progress(precip_contents, desc='Importing precip data')]

    return precip_data


def test():
    test = importPrecipData([4])
    print(test)

if __name__ == '__main__':
    test()
