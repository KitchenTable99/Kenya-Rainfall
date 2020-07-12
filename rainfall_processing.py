# This script will create the rainfall data needed to analyze the economc shocks in Keyna
# Created by Caleb Bitting (Colby class of 2023)
#

from haversine import haversine
import file_parsers as fp

class DHSLocation():

    def __init__(self, center_coords, data_coords):
        '''Init method
        
        Args:
            center_coords (list): a two-element list representing the latitude and longitude of the center of DHSCLUST
            data_coords (list): a 2-D list of coordinate points of the potential data centers
        '''
        self.center = center_coords
        station_distances = [haversine(coord, center_coords) for coord in data_coords]      # haversine calculates dist between points in km
        self.station_indices = [index for index, dist in enumerate(station_distances) if dist <= 40]         # to change the distance needed to include a station, that last number needs to be changed


def test():
    months = fp.cropCalendarParser(404000)
    month_range = list(range(int(months[0]), int(months[1])))

    precip_data = fp.precipFileParser('./resources/precip.1977', month_range, False)

    precip_coords = [row[0] for row in precip_data]
    
    real_precip_coords = [[coord[1], coord[0]] for coord in precip_coords]



    tmep = DHSLocation([0, 38], real_precip_coords)
    print(tmep.station_indices)

if __name__ == '__main__':
    test()
