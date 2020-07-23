# This file will contain all of the methods to parse the various files required to calculate the average rainfall data as well as drought shocks
# Caleb Bitting (Colby Class of 2023)
# Written for research for Professor Daniel LaFave at Colby College
#

import argparse
import itertools
import numpy as np
import pandas as pd

def locationProcessing(percentile_list, rainfall_list):
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
        ryear = float(ryear)/1000
        values.append(pyear < .05)      # 5%-ile
        values.append(pyear < .10)      # 10%-ile
        values.append(pyear < .15)      # 15%-ile
        values.append(round(pyear,2))   # actual %-ile
        values.append(round(ryear, 2))  # rainfall (m)          CHANGE THIS
        total_values.append(values)
    return total_values

def dfProcessing(rain_list, percentile_list, first_year):
    data_list = [locationProcessing(per, rain) for per, rain in zip(percentile_list, rain_list)]
    # change unhelpful index numbers into helpful DHSCLUST -- year
    for location in data_list:
        for year in location:
            tempyr = year[0] + first_year
            year[0] = str(float(data_list.index(location)) + 1)
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

def body(rain_list, percentile_list, year):
    # process data
    data = dfProcessing(rain_list, percentile_list, year)
    df = pd.DataFrame(data=data, columns=['Location', 'Year', '<5%-ile', '<10%-ile', '<15%-ile', '%-ile', 'Total'])

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
    df = body(rain_list, percentile_list, cmd_args.first_year)
    # prepend the dhscc and the dhsyear to the dataframe
    num_rows = len(df.index)
    dhscc = input_df['DHSCC'][0]
    dhsyear = int(input_df['DHSYEAR'][0])
    temp_data = np.array(list(itertools.repeat([dhscc, dhsyear], num_rows)))
    prepend_data = pd.DataFrame(data=temp_data, columns=['DHSCC', 'DHSYEAR'])
    df = pd.concat([prepend_data, df], axis=1)
    # export to csv
    df.to_csv(cmd_args.output_file, index=False)

if __name__ == '__main__':
    main()