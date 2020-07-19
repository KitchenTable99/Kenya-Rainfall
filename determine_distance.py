# This script will provide context for choosing a maximum distance between the center of a precipitation grid and the center of a DHS clust. There are three outputs. Key numbers are dumped into the terminal, a hisogram is plotted, and a csv file is written to the working directory.
# Caleb Bitting (Colby Class of 2023)
# Written for research for Professor Daniel LaFave at Colby College
#

import argparse
import statistics
import pandas as pd
import file_parsers as fp
import matplotlib.pyplot as plt

def commandLineParser():
    '''This function parses the command line arguments
    
    Returns:
        argparse.namespace: an argparse namespace representing the command line arguments
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('shapefile_path', type=str, help='the path to the .shp file in a shapefile folder. This folder should be expanded from a .zip file.')
    parser.add_argument('num_stations', type=int, help='the minimum distance to the (nth) station will be returned. ')
    parser.add_argument('--testing', action='store_true', help='enter testing mode. All functions will be passed testing=True where possible.')
    parser.add_argument('--determine_distance', default=True, help='needed for file_parsers. DO NOT TOUCH.')
    args = parser.parse_args()

    return args

def main():
    # get command-line args
    cmd_args = commandLineParser()
    # bring in station distances
    st_coords = fp.precipFileParser('./resources/precip_data/precip.1977', [4, 8], return_coords=True)
    distances_list = fp.shapeFileParser(cmd_args.shapefile_path, st_coords, cmd_args, testing=cmd_args.testing)
    # sort each location
    for lst in distances_list: lst.sort()
    # create a list of the distance to have cmd_args.num_stations captured
    minimum_distances = [lst[cmd_args.num_stations - 1] for lst in distances_list]
    # output dataframe
    df = pd.DataFrame(minimum_distances, columns=['Distances'])
    df.to_csv('distances.csv', index=False)
    # terminal output
    quartiles = [round(i, 2) for i in statistics.quantiles(minimum_distances)]
    print(f'Q1: {quartiles[0]}\nMedian: {quartiles[1]}\nQ3: {quartiles[2]}')
    print(f'Mean: {round(statistics.mean(minimum_distances), 2)}')
    print(f'Max: {round(max(minimum_distances), 2)}')
    # histogram output
    plt.hist(minimum_distances, bins=len(minimum_distances))
    plt.show()

if __name__ == '__main__':
    main()