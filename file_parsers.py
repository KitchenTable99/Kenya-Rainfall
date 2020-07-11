# This file will contain all of the methods to parse the various files required to calculate the average rainfall data as well as drought shocks
# Caleb Bitting (Colby Class of 2023)
# Written for research for Professor Daniel LaFave at Colby College
import re

def precipFileParser(file_path, months, sum_rainfall):
    '''This function parses a YYYY.precip file.
    
    Args:
        file_path (str): the path to get to the YYYY.precip file
        months (list): the numerical representation of the months to include. (e.g. [5, 6, 7, 8, 9] will keep the months May through September)
        sum_rainfall (bool): whether or not to sum the months kept
    
    Returns:
        3D list: the parsed contents. Of the form [[[x1, y1], may1, june1, july1, august1, september1], [[x2, y2], may2, june2, july2, august2, september2], ... ]
    '''
    # input validation
    if not isinstance(file_path, str): raise TypeError(f'file_path must be a string. You passed a {type(file_path)}.')
    if not isinstance(months, list): raise TypeError(f'months must be a list. You passed a {type(months)}.')
    if not isinstance(sum_rainfall, bool): raise TypeError(f'sum_rainfall must be a boolean. You passed a {type(sum_rainfall)}.')

    # bring in file
    with open(file_path, 'r') as fp:
        raw_file_contents = fp.read()
    # splt into coords and months
    # split into rows and then split by spaces. drop all items that are the empty string
    file_contents = raw_file_contents.split('\n')
    file_contents = [row.split(' ') for row in file_contents]
    drop_contents = [dropEmptyString(row) for row in file_contents]
    # drop any list at the very end that is the empty list
    while drop_contents[-1] == []:
        drop_contents.pop()
    # turn everything into a float
    drop_contents = floatify(drop_contents)
    # separate the coordinate pairs from the rainfall data
    file_contents = []
    for row in drop_contents:
        temp_row = []
        temp_row.append([row[0], row[1]])       # coordinate pair
        for item in row[2:]:                    # add the rest of the items one by one
            temp_row.append(item)
        file_contents.append(temp_row)
    # filter out irrelevant months
    months.append(0)
    month_filter = [[row[index] for index in range(len(row)) if index in months]for row in file_contents]
    # sum if desired
    if sum_rainfall:
        sum_list = []
        for row in file_contents:
            temp_row = []
            temp_row.append(row[0])
            total = sum(row[1:])
            temp_row.append(total)
            sum_list.append(temp_row)
        return sum_list                        # the return statement in the case sum_ranfall == True


    return month_filter                        # the return statement in the case sum_rainfall == False

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
    '''Drops every instance of the empty string in a list
    
    Args:
        lst (list): pre-processed list with empty strings potentially present
    
    Returns:
        list: the same input lst but with all empty strings dropped
    '''
    processed = [item for item in lst if item != '']
    return processed

def cropCalendarParser(unit_name_start, crop_cal_name='./resources/cropping_calendar_rainfed.txt'):
    '''This function parses the crop calendar to obtain the growing season of the predominant crop in a certain area.
    
    Args:
        unit_name_start (int): the unit code for the desired country/area.
        crop_cal_name (str, optional): the path to the crop calendar. Defaults to './resources/cropping_calendar_rainfed.txt'
    
    Returns:
        tuple: the beginning and end of the growing season as strings. e.g. ('4', '8')
    '''
    # bring in calendar
    with open(crop_cal_name, 'r') as fp:
        calendar_contents = fp.read()
    # only keep lines starting with correct unit code
    pattern = re.compile(fr'\b{unit_name_start}\s+\d+\s\d+[^\n\d]+(\d+.\d*)\s+(\d+)\s+(\d+).*')     # looks for the exact pattern that the lines take and groups the area, beginning month, and end month for easy access later
    matches = pattern.finditer(calendar_contents)
    # pull out areas and find the largest
    areas = [match.group(1) for match in matches]
    areas = floatify(areas)
    largest_index = areas.index(max(areas))
    # create growing season tuples and return the largest
    matches = pattern.finditer(calendar_contents)
    growing_seasons = [(match.group(2), match.group(3)) for match in matches]

    return growing_seasons[largest_index]

def test():
    test = cropCalendarParser(404000)
    print(test) 

if __name__ == '__main__':
    test()