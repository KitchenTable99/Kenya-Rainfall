# This script will provide context for choosing a maximum distance between the center of a precipitation grid and the center of a DHS clust. There are three outputs. Key numbers are dumped into the terminal, a hisogram is plotted, and a csv file is written to the working directory.
# Caleb Bitting (Colby Class of 2023)
# Written for research for Professor Daniel LaFave at Colby College
#

import os
import math
import pickle
import argparse
import statistics
import numpy as np
import pandas as pd
import file_parsers as fp
import csv_polishing as cp
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

def commandLineParser():
    '''This function parses the command line arguments
    
    Returns:
        argparse.namespace: an argparse namespace representing the command line arguments
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('num_stations', type=int, help='the minimum distance to the (nth) station will be returned. ')
    parser.add_argument('--graph', action='store_true', help='whether or not to graph the distance data')
    parser.add_argument('--distance_csv', action='store_true', help='whether or not to dump the distance data to a csv')
    parser.add_argument('--no_pickle', action='store_false', help='whether or not to pickle the distance list')
    parser.add_argument('--testing', action='store_true', help='enter testing mode. All functions will be passed testing=True where possible.')
    args = parser.parse_args()

    return args

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

def main():
    # get command-line args
    cmd_args = commandLineParser()
    cmd_args.determine_distance = True
    cmd_args.pickle = False
    # add screen width
    _, columns = os.popen('stty size', 'r').read().split()
    cmd_args.screen_width = int(columns)
    # get shapefile
    cmd_args.shapefile_path = getFile('.shp', 'shapefile', cmd_args)
    # bring in station distances
    st_coords = fp.precipFileParser('./resources/precip_data/precip.1977', [4, 8], return_coords=True)
    raw_distances_list = fp.shapeFileParser(cmd_args, st_coords, testing=cmd_args.testing)
    if cmd_args.no_pickle:
        pass
    else:
        with open('distance_list.pickle', 'wb') as f:
            pickle.dump(raw_distances_list, f)
    # drop the ones at the origin
    clust_nums = cp.interpretOriginLog('origin_log.csv')
    os.system('rm origin_log.csv')
    clust_indices = [clust_num - 1 for clust_num in clust_nums]
    distances_list = [raw_dist for index, raw_dist in enumerate(raw_distances_list) if index not in clust_indices]
    # sort each location
    for lst in distances_list: lst.sort()
    # create a list of the distance to have cmd_args.num_stations captured
    minimum_distances = [lst[cmd_args.num_stations - 1] for lst in distances_list]
    if cmd_args.distance_csv:
        # output dataframe
        df = pd.DataFrame(minimum_distances, columns=['Distances'])
        df.to_csv('distances.csv', index=False)
    # terminal output
    quartiles = [round(i, 2) for i in statistics.quantiles(minimum_distances)]
    print(f'Q1: {quartiles[0]}\nMedian: {quartiles[1]}\nQ3: {quartiles[2]}')
    print(f'Mean: {round(statistics.mean(minimum_distances), 2)}')
    print(f'Max: {round(max(minimum_distances), 2)}')
    if cmd_args.graph:
        # histogram output
        bin_num = int(1 + 3.322*math.log10(len(minimum_distances)))
        plt.hist(minimum_distances, weights=np.ones(len(minimum_distances)) / len(minimum_distances), bins=bin_num)
        plt.xlabel('Distance Value')
        plt.title('Determine Distance')
        plt.ylabel('Percentage of total DHS Clusters')
        plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
        plt.show()

if __name__ == '__main__':
    main()