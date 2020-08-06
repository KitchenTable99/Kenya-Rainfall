# This script will gather the rainfall data and organize it by percentile
# Caleb Bitting (Colby Class of 2023)
# Written for research for Professor Daniel LaFave at Colby College
#

# dependencies
import os
import pickle
import argparse
import itertools
import statistics
import numpy as np
import pandas as pd
import file_parsers as fp
import scipy.stats as stats
from termcolor import cprint
from tqdm import tqdm as progress

# small utility functions
def getNum(biggest, name):
    '''Gets a user input number
    
    Args:
        biggest (int): largest number a user can enter
        name (str): what the user is entering
    
    Returns:
        int: the number the user entered
    '''
    usr_inp = input(f'{name.capitalize()} number:  ')
    if int(usr_inp) > biggest:
        getNum(biggest)

    return int(usr_inp)

def getFile(extention, name, cmd_args):
    '''Finds files and returns user chosen path
    
    Args:
        extention (str): the .extention of the desired file type (e.g. .pdf, .txt, .pickle)
        name (str): what to call the file when prompting the user
        cmd_args (argparse.namespace): command-line argumentss
    
    Returns:
        str: the path of the chosen file
    
    Raises:
        Exception: If there are no files of the desired type found, raises Exception
    '''
    # find shapefiles recursively
    disp_name = []
    paths = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(extention):
                disp_name.append(file)                                 # name for display
                paths.append(os.path.join(root, file))                 # path for later use
    if len(disp_name) == 0:
        raise Exception(f'No {name}s were found.')
    else:
        printClearLine(cmd_args)
        print(f'Which {name} would you like to use?')
        for index, shapefile in enumerate(disp_name):
            print(f'[{index+1}]\t{shapefile}')

    usr_shp_file = getNum(len(disp_name), name)

    return paths[usr_shp_file - 1]

def printClearLine(cmd_args):
    '''Prints a dashed line across the terminal window.
    
    Args:
        cmd_args (argparse.namespace): contains the width of the terminal window
    '''
    fancy_sep = ['-' for _ in range(cmd_args.screen_width)]
    print(''.join(fancy_sep)) 

def commandLineParser():
    '''This function parses the command line arguments
    
    Returns:
        argparse.namespace: an argparse namespace representing the command line arguments
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('unit_code', type=int, help='the unit code that designates the area of interest. See ./resources/unit_name.txt for list of unit codes.')
    parser.add_argument('distance', type=float, help='the maximum distance (in km) allowed between a DHS center and a precip grid center.')
    parser.add_argument('len_years', type=int, help='the number of years to use to fit each gamma distribution.')
    parser.add_argument('--output_file', type=str, default='rainfall_data.csv', help='the name of the processed csv. Defaults to rainfall_data.csv')
    parser.add_argument('--pickle', action='store_true', help='whether or not to read a pickle for the distance data')
    parser.add_argument('--testing', action='store_true', help='enter testing mode. All functions will be passed testing=True where possible.')
    args = parser.parse_args()

    return args

# rainfall sum functions
def sumRain(index_list, precip_data):
    '''This function generates all rainfall sums for a particular location.
    
    Args:
        index_list (list): all of the relevant indices. 'Station Indices' column in GeoDataFrame.
        precip_data (list): 2-D list of all rainfall data. Returned by fp.precipFileParser()
    
    Returns:
        list: the sums for every rainfall year of the relevant stations. Of the form [sum1, sum2, sum3, ...]
    '''
    rainfall_totals = [[item for index, item in enumerate(lst) if index in index_list] for lst in precip_data]
    return rainfall_totals

def importPrecipData(month_range, testing=False):
    '''This function imports all precip data in ./resources/precip_data or another specified folder
    
    Args:
        month_range (list): a list of months across which to sum the rainfall
        precip_data_folder (str, optional): a string representing the path to the folder in which all of the .precip files are stored. Defaults to './resources/precip_data'
        testing (bool, optional): wheter or not the function is in testing mode. If so, only the first ten precip files will be considered for speed. Defaults to False
    
    Returns:
        list: a list of parsed precip data. Of the form [[[x1, y1], SUM2], [[x2, y2], SUM2], ...] where SUM is the sum of the rainfall in the selected months
    '''
    # get list of precip files
    precip_files = []
    for root, dirs, files in os.walk('./resources/precip_data'):
        for file in files:
            if file.startswith('precip'):
                precip_files.append(os.path.join(root, file))
    # if testing:
        # precip_files = precip_files[:10]
    # create precip data list for them all
    precip_data = [fp.precipFileParser(path, month_range) for path in progress(precip_files, desc='Importing precip data')]

    return precip_data

def getRainSums(cmd_args):
    '''This function runs the main functionality
    
    Args:
        cmd_args (argparse.Namespace): an argparse namespace
    
    Returns:
        GeoDataFrame: a GeoPandas GeoDataFrame with all of the rainfall sums included.
    '''
    # parse month range
    month_range = fp.cropCalendarParser(cmd_args.unit_code)
    month_range = [int(month) for month in month_range]
    # get precip data
    # precip_data = importPrecipData(month_range, testing=cmd_args.testing)
    with open('precip.pickle', 'rb') as f:
        precip_data = pickle.load(f)
    # get geodata
    st_coords = fp.precipFileParser('./resources/precip_data/precip.1977', [4, 8], return_coords=True)
    gdf = fp.shapeFileParser(cmd_args, st_coords, testing=cmd_args.testing)
    # generate rainfall totals
    station_indices = gdf['Station Indices'].tolist()
    rainfall_totals = [sumRain(index_list, data) for index_list, data in progress(zip(station_indices, itertools.repeat(precip_data)), total=len(gdf['Station Indices']), desc='Calculating rainfall sums')]
    gdf['Rainfall Totals'] = rainfall_totals
    # print out needed calculation stats
    station_lengths = [len(lst) for lst in station_indices]     # how many stations were captured
    printClearLine(cmd_args)
    print(f'The average number of captured stations was {round(statistics.mean(station_lengths), 2)}')
    if 0 in station_lengths:                                    # warn if any location didn't capture data
        cprint('::ATTENTION::', 'red', attrs=['reverse', 'blink'])
        print(f'{station_lengths.count(0)}/{len(station_lengths)} locations did not capture a single precip station. This will *likely* be addressed in the final csv file.')
    else: print('Every location captured at least one precip station.')

    return gdf

# gamma fitting functions
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

def sumSlicing(sum_list, len_years):
    '''This function generates all percentiles across a list.
    
    Args:
        sum_list (list): a list containing all the rainfall sum data.
        len_years (int): how many years to fit a gamma distribution
    
    Returns:
        list: a list of percentiles fitted to a gamma distribution
    '''
    leading_pointer = 0
    okazaki_pointer = len_years + 1
    percentile_list = []
    while okazaki_pointer <= len(sum_list):                         # iterate over every slice of the list that allows for adequate length
        data = sum_list[leading_pointer:okazaki_pointer]
        temp = percentile(data)
        percentile_list.append(temp)
        leading_pointer += 1
        okazaki_pointer += 1

    return percentile_list

# csv polishing functions
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
    '''Modifies the DataFrame to the desired format
    
    Args:
        rain_list (list): the list of the rainfall totals
        percentile_list (list): the list of the corresponding percentiles
        first_year (int): the first year of observed data
        cmd_args (argparse.namespace): the command-line arguments
    
    Returns:
        np.array: returns an array of the data
    '''
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

def logInterpreter(file_path='origin_log.csv'):
    '''This function turns the origin csv into something that makes sense
    
    Args:
        file_path (str, optional): the file path containing the origin csv
    '''
    # get which clusters were dropped
    try:
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
    except Exception as e:
        pass

def interpretOriginLog(file_path):
    '''Get the clusters to drop
    
    Args:
        file_path (str): file path representing origin_log
    
    Returns:
        list: a list of integers of the cluster numbers to drop
    '''
    # get clusters to drop
    try:
        with open(file_path, 'r') as f:
            contents = f.read()
        list_contents = contents.split('\n')
        list_contents.pop()
        int_contents = [int(item) + 1 for item in list_contents]
    except Exception:
        int_contents = []

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

def main(pickle_data=False):
    # get command line arguments
    cmd_args = commandLineParser()
    cmd_args.determine_distance = False
    # add screen width
    _, columns = os.popen('stty size', 'r').read().split()
    cmd_args.screen_width = int(columns)
    # get shapefile
    cmd_args.shapefile_path = getFile('.shp', 'shapefile', cmd_args)
    if cmd_args.pickle:
        cmd_args.pickle = getFile('.pickle', 'pickle', cmd_args)

    # obtain rainfall sums in DataFrame
    gdf = getRainSums(cmd_args)
    gdf.to_csv('un_sumBad.csv')
    return
    printClearLine(cmd_args)
    # dump data if requested
    if pickle_data:
        with open('rain.pickle', 'wb') as f:
            pickle.dump(gdf, f)
    '''
    with open('rain.pickle', 'rb') as f:
        gdf = pickle.load(f)
    '''
    # get rainfall totals
    rainfall_sums = gdf['Rainfall Totals'].tolist()
    # calculate percentiles
    percentiles = [sumSlicing(rainfall_sum, cmd_args.len_years) for rainfall_sum in progress(rainfall_sums, desc='Calculating Percentiles')]
    gdf['Rainfall Percentiles'] = percentiles
    # dump data if requested
    if pickle_data:
        with open('gamma.pickle', 'wb') as f:
            pickle.dump(gdf, f)
    '''
    with open('gamma.pickle', 'rb') as f:
        gdf = pickle.load(f)
    rainfall_sums = gdf['Rainfall Totals'].tolist()
    percentiles = gdf['Rainfall Percentiles'].tolist()
    '''
    # edit csv
    starting_year = 1950 + cmd_args.len_years
    data = dfProcessing(rainfall_sums, percentiles, starting_year, cmd_args)
    df = pd.DataFrame(data=data, columns=['Location', 'Year', '<5%-ile', '<10%-ile', '<15%-ile', '%-ile', 'Total Rainfall (mm)'])
    df = dropOrigin(df)
    logInterpreter()
    # get DHSID
    DHSID_col = gdf['DHSID'].repeat(len(percentiles[0]))
    DHSID_col = DHSID_col.reset_index(drop=True)
    df.insert(0, 'DHSID', DHSID_col, allow_duplicates=True)
    df.drop('Location', axis=1, inplace=True)
    # output
    df.to_csv(cmd_args.output_file, index=False)

if __name__ == '__main__':
    main(True)
