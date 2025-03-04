# This file will contain all of the methods to parse the various files required to calculate the average rainfall data as well as drought shocks
# Caleb Bitting (Colby Class of 2023)
# Written for research for Professor Daniel LaFave at Colby College
#

import os
import re
import time
import itertools
import geopandas as gpd
from haversine import haversine
from tqdm import tqdm as progress

def timeIt(f):
    '''This decorator times a function.
    '''
    def wrapper(*args, **kwargs):
        start = time.time()
        print('timeIt decorator called')
        output = f(*args, **kwargs)
        end = time.time()
        print(f'{f.__name__} took {end - start} seconds to run.')        # time it
        return output

    return wrapper
    
def pointDist(point1, pointlist, index):
    '''This function calculates the distance between one point and a list of others
    
    Args:
        point1 (shapely.geometry.Point): the point against which to calculate all of the distances
        pointlist (list): a list of shapely.geometry.Point objecsts against which the distances are calculated
    
    Returns:
        list: a list of distances between the two points as if they were in meters
    '''
    latitude = point1.y
    longitude = point1.x
    # filter out the origin points
    if latitude == 0 and longitude == 0:
        with open('origin_log.csv', 'a') as f:
            f.write(str(index)+'\n')
    distances = [haversine((latitude, longitude), point2) for point2 in pointlist]       # uses methods built into shapely.geometry
    return distances

def precipListParser(file_path, testing=False):
    '''This function parses the list of precip names
    
    Args:
        file_path (str): a string representing the path to the file containing the names of the precip files. Defaults to the empty string.
        testing (bool, optional): whether or not to only keep the first ten precip files.
    
    Returns:
        list: a list of the names of the precip files.
    '''
    with open(file_path, 'r') as f:
        precip_contents = f.read()
    precip_contents = precip_contents.split('\n')
    precip_contents.pop()
    if testing:
        precip_contents = precip_contents[:10]      # only take the first ten items if testing is passed as True

    return precip_contents

def shapeFileParser(file_path, station_coords, cmd_args, testing=False):
    '''This function onboards the shapefile data to create the necessary railfall data
    
    Args:
        file_path (string): a file path to the .shp file in the unzipped .zip shapefile folder
        station_coords (list): a list generated by the stationCoords function
        cmd_args (argparse.Namespace): a namespace to grab command-line arguments
        testing (bool, optional): whether or not the function is being tested. If passed as True, only the first ten locations will be used for the sake of speed. Defaults to False
    
    Returns:
        Geopandas.GeoDataFrame: a GeoDataFrame with all of the shapefile data plus a column ('Station Indices') containing a list of relevant indicies of the precip file data over which to search
    '''
    # import shapefile
    gdf = gpd.read_file(file_path)
    # only take the first ten rows if testing (for speed)
    if testing:
        gdf = gdf.iloc[:100]
    # create a list of shapely.geometry.Point objects for distance comparison
    latlong_coord_tuples = [(coord_list[1], coord_list[0]) for coord_list in station_coords]
    # find the distance between center coord and every station (print out progress bar)
    alldist = [pointDist(geom, lst, index) for index, (geom, lst) in progress(enumerate(zip(gdf['geometry'], itertools.repeat(latlong_coord_tuples))), total=len(gdf['geometry']), desc='Importing shapefile')]
    if cmd_args.determine_distance: return alldist
    # create a new column and assign it the relevant station indices
    monitor_stations = [[index for index, dist in enumerate(row) if dist <= cmd_args.distance] for row in alldist]
    gdf['Station Indices'] = monitor_stations

    return gdf

def precipFileParser(file_path, months, sum_rainfall=True, return_coords=False):
    '''This file pulls out the rainfall data in a specific precip.YYYY file.
    
    Args:
        file_path (string): a string representing the path to the precip.YYYY file to be parsed
        months (list): a two-element list of the numeric value of the start month and the numeric value of the end month
        sum_rainfall (bool, optional): whether or not to sum the rainfall data. Defaults to True
        return_coords (bool, optional): whether to return rainfall data or coordinate values. Defaults to False (data returned).
    
    Returns:
        list: if return_coords is passed as True, the return value will be a two-dimentional list of the form [[x1, y1], [x2, y2], ...].
              if sum_rainfall is passed as True, the return value will be a one-dimentional list of the total rainfall (in mm) that fell during the span of the months passed.
              If sum_rainfall is passed as False, the return value will be a two-dimentional list of the monthly rainfall values (in mm) for each station during the desired month ran
    '''
    # input validation
    if not isinstance(file_path, str): raise TypeError(f'file_path must be a string. You passed a {type(file_path)}.')
    if not isinstance(months, list): raise TypeError(f'months must be a list. You passed a {type(months)}.')
    if len(months) != 2: raise ValueError(f'months must be a list of length two. You passed a list of length {len(months)}.')
    if not isinstance(sum_rainfall, bool): raise TypeError(f'sum_rainfall must be a boolean. You passed a {type(sum_rainfall)}.')
    if not isinstance(return_coords, bool): raise TypeError(f'return_coords must be a boolean. You passed a {type(return_coords)}.')

    # bring in file
    with open(file_path, 'r') as fp:
        raw_file_contents = fp.read()
    file_contents = raw_file_contents.split('\n')                   # create rows
    # return coords if that's the desired item
    if return_coords:
        file_contents = [row[:16] for row in file_contents]             # only keep coords
        file_contents = [row.split(' ') for row in file_contents]       # split long, lat coords
        file_contents = dropEmptyString(file_contents)                  # drop empty strings
        while file_contents[-1] == []:                                  # drop trailing empty lists
            file_contents.pop()                                             
        file_contents = floatify(file_contents)                         # turn into floats
        return file_contents
    else:       # return data most time though
        # pull out rainfall data
        file_contents = [row[16:] for row in file_contents]             # get rid of coords
        file_contents = [row.split(' ') for row in file_contents]       # split monthly rainfall
        file_contents = dropEmptyString(file_contents)                  # drop empty strings
        while file_contents[-1] == []:                                  # drop trailing empty lists
            file_contents.pop()                                             
        file_contents = floatify(file_contents)                         # turn into floats
        # filter out irrelevant months
        pointer = months[0] - 1             # index of start month
        month_filter = [pointer]
        while pointer != months[1] - 1:     # add every index until the index of the end month is reached. Wrap at 11.
            if pointer == 11:
                pointer = 0
            else:
                pointer += 1
            month_filter.append(pointer)
        # sum rainfall if desired
        if sum_rainfall:
            sum_data = [sum([item for index, item in enumerate(row) if index in month_filter]) for row in file_contents]

            return sum_data

        return [[item for index, item in enumerate(row) if index in month_filter] for row in file_contents]        # the return statement in the case sum_rainfall == False

def cropCalendarParser(unit_name_start, crop_cal_name='./resources/cropping_calendar_rainfed.txt'):
    '''This function parses the crop calendar to obtain the growing season of the predominant crop in a certain area.
    
    Args:
        unit_name_start (int): the unit code for the desired country/area. See ./resources/unit_name.txt for list of unit codes.
        crop_cal_name (str, optional): the path to the crop calendar. Defaults to './resources/cropping_calendar_rainfed.txt'
    
    Returns:
        tuple: the beginning and end of the growing season as strings. e.g. ('4', '8')
    '''
    # input validation
    if not isinstance(unit_name_start, int): raise TypeError(f'unit_name_start must be a integer. You passed a {type(unit_name_start)}.')
    if not isinstance(crop_cal_name, str): raise TypeError(f'crop_cal_name must be a string. You passed a {type(crop_cal_name)}.')

    # bring in calendar
    with open(crop_cal_name, 'r') as fp:
        calendar_contents = fp.read()
    # only keep lines starting with correct unit code
    pattern = re.compile(fr'\b{unit_name_start}\s+\d+\s\d+[^\n\d]+(\d+.\d*)\s+(\d+)\s+(\d+).*')     # looks for the exact pattern that the lines take and groups the area, beginning month, and end month for easy access later (regex expression)
    matches = pattern.finditer(calendar_contents)
    # pull out areas and find the largest
    areas = [match.group(1) for match in matches]
    areas = floatify(areas)
    largest_index = areas.index(max(areas))
    # create growing season tuples and return the largest
    matches = pattern.finditer(calendar_contents)
    growing_seasons = [[match.group(2), match.group(3)] for match in matches]

    return growing_seasons[largest_index]

def floatify(lst):
    '''This function turns every item in a list into a float. If a nested list is passed, the function will be called recursively on the inside lists.
    
    Args:
        lst (list): the list containing the items to turn into floats
    
    Returns:
        list: the exact same input lst but with each item as a float
    '''
    # iterate over every item in the list
    for index, item in enumerate(lst):
        # if the item in the list is a list itself, recursively call the function
        if isinstance(item, list):
            floatify(item)
        else:
            # turn into a float
            lst[index] = float(item)

    return lst

def dropEmptyString(lst):
    '''Drops every instance of the empty string in a list. Calls recursively if a multi-dimentional list is passed.
    
    Args:
        lst (list): pre-processed list with empty strings potentially present
    
    Returns:
        list: the same input lst but with all empty strings dropped
    '''
    complete_list = []
    for item in lst:
        if isinstance(item, list):
            complete_list.append(dropEmptyString(item))
        elif item != '':
            complete_list.append(item)

    return complete_list

def test():
    st_coords = precipFileParser('./resources/precip_data/precip.1977', [4, 8], return_coords=True)
    gdf = shapeFileParser('./resources/kenya_dhs_2013/KEGE43FL.shp', st_coords)

if __name__ == '__main__':
    test()