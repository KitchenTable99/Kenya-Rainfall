# This file will contain all of the methods to parse the various files required to calculate the average rainfall data as well as drought shocks
# Caleb Bitting (Colby Class of 2023)
# Written for research for Professor Daniel LaFave at Colby College
#

import os
import json
import argparse
import pandas as pd
import scipy.stats as stats
from tqdm import tqdm as progress

def percentile(data_list):
    '''This function calculates a percentile value in a fitted gamma distribution.
    
    Args:
        data_list (list): a list of data across which to fit the gamma distribution. The last value in the list will not be included in the fitting process and will be used as the target value to find the percentile.
    
    Returns:
        TYPE: DESCRIPTION
    '''
    target_value = data_list.pop()  # take the target value out of the data list
    fit_alpha, fit_loc, fit_beta=stats.gamma.fit(data_list)

    return stats.gamma.cdf(target_value, fit_alpha, loc=fit_loc, scale=fit_beta)

def sumSlicing(sum_list, len_years, verbose=False):
    '''This function generates all percentiles across a list.
    
    Args:
        sum_list (list): a list containing all the rainfall sum data.
        len_years (int): how many years to fit a gamma distribution
    
    Returns:
        list: a list of percentiles fitted to a gamma distribution
    '''
    if verbose: pbar = progress(total=len(sum_list)-len_years, leave=False)     # establish a nice progress bar
    leading_pointer = 0
    okazaki_pointer = len_years + 1
    percentile_list = []
    while okazaki_pointer <= len(sum_list):                         # iterate over every slice of the list that allows for adequate length
        data = sum_list[leading_pointer:okazaki_pointer]
        temp = percentile(data)
        percentile_list.append(temp)
        leading_pointer += 1
        okazaki_pointer += 1
        if verbose: pbar.update(1)  # update progress bar
    if verbose: pbar.close()

    return percentile_list

def commandLineParser():
    '''This function parses the command line arguments
    
    Returns:
        argparse.namespace: an argparse namespace representing the command line arguments
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('file_path', type=str, help='the path to the csv file containing the output of sum_rainfall.py')
    parser.add_argument('len_years', type=int, help='the number of years to use to fit each gamma distribution.')
    parser.add_argument('--verbose', '-v', action='store_true', help='whether or not to see the intermediate progress bar')
    parser.add_argument('--testing', '-t', action='store_true', help='whether or not to see the intermediate progress bar')
    args = parser.parse_args()

    return args

def body(sum_list, cmd_args):
    # calculate percentiles
    rainfall_percentiles = [sumSlicing(rainfall_sum, cmd_args.len_years, cmd_args.verbose) for rainfall_sum in progress(sum_list, desc='Calculating Percentiles')]
    if cmd_args.verbose or __name__ == '__main__':
        # print out year range
        _, columns = os.popen('stty size', 'r').read().split()
        fancy_sep = ['-' for _ in range(int(columns))]
        print(''.join(fancy_sep))                                   # allow for some eyeball breathing room
        print(f'This program calculated {len(rainfall_percentiles[0])} years worth of percentiles.\nThe list stored in "Rainfall Percentiles" represents data beginning in the year {1950+cmd_args.len_years}.\nThis is assuming that the first precip file contains data from the year 1950.')

    return rainfall_percentiles

def main():
    # import needed materials
    cmd_args = commandLineParser()
    df = pd.read_csv(cmd_args.file_path)
    # just take the rainfall totals
    rainfall_sums = df['Rainfall Totals'].tolist()
    # turn the strings into lists
    rainfall_sums = [json.loads(rainfall_sum) for rainfall_sum in rainfall_sums]
    # get data into dataframe
    if cmd_args.testing:
        percentiles = body(rainfall_sums[:3], cmd_args)
        df = df.truncate(before=0, after=2)
    else:
        percentiles = body(rainfall_sums, cmd_args)
    df['Rainfall Percentiles'] = percentiles
    # write out
    write_path = 'gammaProcessed_' + cmd_args.file_path
    df.to_csv(write_path, index=False)


if __name__ == '__main__':
    main()



