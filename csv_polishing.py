# This file will contain all of the methods to parse the various files required to calculate the average rainfall data as well as drought shocks
# Caleb Bitting (Colby Class of 2023)
# Written for research for Professor Daniel LaFave at Colby College
#

import os
import argparse
import itertools
import numpy as np
import pandas as pd

def locationProcessing(percentile_list, rainfall_list, cmd_args):
    '''This function turns the rainfall totals and precipitation percentiles into the desired form.
    
    Args:
        percentile_list (list): the percentiles for a given location
        rainfall_list (list): the rainfall totals for a given locatioin
    
    Returns:
        list: the interpeted data
    '''
    total_values = []
    for pyear, ryear in zip(percentile_list, rainfall_list):
        values = []
        values.append(percentile_list.index(pyear))
        pyear = float(pyear)
        ryear = rainfall_list[rainfall_list.index(ryear) + cmd_args.len_years]
        values.append(pyear < .05)      # 5%-ile
        values.append(pyear < .10)      # 10%-ile
        values.append(pyear < .15)      # 15%-ile
        values.append(round(pyear,4))   # actual %-ile
        values.append(round(float(ryear), 4))  # rainfall (mm)          CHANGE THIS
        total_values.append(values)
    return total_values

def dfProcessing(rain_list, percentile_list, first_year, cmd_args):
    data_list = [locationProcessing(per, rain, cmd_args) for per, rain in zip(percentile_list, rain_list)]
    # change unhelpful index numbers into helpful DHSCLUST -- year
    for location in data_list:
        for year in location:
            tempyr = year[0] + first_year
            year[0] = str(int(data_list.index(location)) + 1)
            year.insert(1, str(tempyr))
    # create numpy array
    shape = (len(data_list[0])*len(data_list))
    data_array = np.array(data_list).reshape(shape, 7)
    
    return data_array

def commandLineParser():
    '''This function parses the command line arguments
    
    Returns:
        argparse.namespace: an argparse namespace representing the command line arguments
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('file_path', type=str, help='the path to the csv file containing the output of gamma_calculations.py')
    parser.add_argument('--first_year', type=int, default=1980, help='the year corresponding to the first value of the precipitation percentile. Output by gamma_calculations.py. Defaults to 1980')
    parser.add_argument('--output_file', '-n', type=str, default='cleanGamma_data.csv', help='the name of the processed csv. Defaults to cleanGamma_data.csv')
    args = parser.parse_args()

    return args

def logInterpreter(file_path='origin_log.csv'):
    '''This function turns the origin csv into something that makes sense
    
    Args:
        file_path (str, optional): the file path containing the origin csv
    '''
    # get which clusters were dropped
    with open(file_path, 'r') as f:
        contents = f.read()
    list_contents = contents.split('\n')
    list_contents.pop()
    clust_nums = [int(list_content) + 1 for list_content in list_contents]
    # print it out and write it to a file
    out_str = f'The clusters that had to be dropped were {clust_nums}.'
    print(out_str + '\nThis is written in a file called origin_log.txt')
    with open('origin_log.txt', 'w') as fp:
        fp.write(out_str)
    os.system(f'rm {file_path}')

def interpretOriginLog(file_path):
    '''Get the clusters to drop
    
    Args:
        file_path (str): file path representing origin_log
    
    Returns:
        list: a list of integers of the cluster numbers to drop
    '''
    # get clusters to drop
    with open(file_path, 'r') as f:
        contents = f.read()
    list_contents = contents.split('\n')
    list_contents.pop()
    int_contents = [int(item) + 1 for item in list_contents]

    return int_contents

def dropOrigin(df, file_path='origin_log.csv'):
    '''This drops any point that was at the origin
    
    Args:
        df (pd.DataFrame): the dataframe containing the data
        file_path (str, optional): the csv file with the indicies of the rows to drop
    
    Returns:
        pd.DataFrame: the same dataframe that was the input with the necessary columns dropped
    '''
    int_contents = interpretOriginLog(file_path)
    # determine corresponding indicies
    # num rows per clust
    df_length = len(df.index)
    num_clust = float(df['Location'].iloc[df_length - 1])
    cols_per_clust = df_length/num_clust
    # start and end points
    start_points = [(num - 1) * cols_per_clust for num in int_contents]
    end_points = [num*cols_per_clust for num in int_contents]           # purposefully one number over needed index due to exclusivity of range()
    # create range lists
    range_list = [list(range(int(p1), int(p2))) for p1, p2 in zip(start_points, end_points)]
    flat_list = list(itertools.chain.from_iterable(range_list))
    # drop columns and reindex
    df.drop(flat_list, axis=0, inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df

def body(rain_list, percentile_list, year, cmd_args):
    # process data
    data = dfProcessing(rain_list, percentile_list, year, cmd_args)
    df = pd.DataFrame(data=data, columns=['Location', 'Year', '<5%-ile', '<10%-ile', '<15%-ile', '%-ile', 'Total Rainfall (mm)'])
    df = dropOrigin(df)
    logInterpreter()

    return df

def main():
    # import needed data
    cmd_args = commandLineParser()
    input_df = pd.read_csv(cmd_args.file_path)
    # get the lists out of the df
    percentile_list = input_df['Rainfall Percentiles'].tolist()
    percentile_list = [item.strip('][').split(', ') for item in percentile_list]
    rain_list = input_df['Rainfall Totals'].tolist()
    rain_list = [item.strip('][').split(', ') for item in rain_list]
    # process
    df = body(rain_list, percentile_list, cmd_args.first_year, cmd_args)
    # get DHSID
    DHSID_col = input_df['DHSID'].repeat(len(percentile_list[0]))
    DHSID_col = DHSID_col.reset_index(drop=True)
    df.insert(0, 'DHSID', DHSID_col, allow_duplicates=True)
    df.drop('Location', axis=1, inplace=True)
    # export to csv
    df.to_csv(cmd_args.output_file, index=False)

if __name__ == '__main__':
    main()