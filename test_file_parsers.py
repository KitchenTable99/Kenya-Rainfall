# unittest file for file_parsers

import pickle
import unittest
from shapely.geometry import Point
from file_parsers import cropCalendarParser
from file_parsers import pointDist
from file_parsers import getShapeFile
from file_parsers import precipFileParser
from file_parsers import coordTuples
from file_parsers import getDistList
from file_parsers import shapeFileParser

def loadPickle(path):
    with open(path, 'rb') as fp:
        correct = pickle.load(fp)

    return correct

class Parameters():

    def __init__(self, file_path, testing, pickle, dd=False, distance=None):
        self.shapefile_path = file_path
        self.testing = testing
        self.pickle = pickle
        self.determine_distance = dd
        self.distance = distance

class SHPFileTester(unittest.TestCase):

    def test_coordTuples(self):
        self.assertEqual(coordTuples([[3, 5],[-10, -5],[1, -10],[-3, 59.7], [0, 1], [3, 0]]), [(5, 3), (-5, -10), (-10, 1), (59.7, -3), (1, 0), (0, 3)])

    def test_distListNoPickle(self):
        cmd_args = Parameters('', '', False)
        gdf = loadPickle('./resources/testing_files/correct_shortened.pickle')
        latlongs = [(5, 3), (-5, -10), (-10, 1), (59.7, -3), (1, 0), (0, 3)]
        correct = loadPickle('./resources/testing_files/correct_noPickleDistList.pickle')
        self.assertEqual(getDistList(cmd_args, gdf, latlongs), correct)

    def test_distListPickle(self):
        cmd_args = Parameters('', '', './resources/testing_files/correct_noPickleDistList.pickle')
        correct = loadPickle('./resources/testing_files/correct_noPickleDistList.pickle')
        self.assertEqual(getDistList(cmd_args, None, None), correct)

    def test_determineDistance(self):
        cmd_args = Parameters('./resources/testing_files/shortened.shp', False, './resources/testing_files/correct_noPickleDistList.pickle', dd=True)
        coords = [(5, 3), (-5, -10), (-10, 1), (59.7, -3), (1, 0), (0, 3)]
        correct = loadPickle('./resources/testing_files/correct_noPickleDistList.pickle')
        self.assertEqual(shapeFileParser(cmd_args, coords), correct)

    def test_normalFunction(self):
        cmd_args = Parameters('./resources/testing_files/shortened.shp', False, './resources/testing_files/correct_noPickleDistList.pickle', distance=4100)
        coords = [(5, 3), (-5, -10), (-10, 1), (59.7, -3), (1, 0), (0, 3)]
        correct = loadPickle('./resources/testing_files/correct_shapefile.pickle')
        self.assertTrue(shapeFileParser(cmd_args, coords).equals(correct))


class CropTester(unittest.TestCase):

    def test_growingSeasons(self):
        self.assertEqual(cropCalendarParser(64000), ['6', '10'])
        self.assertEqual(cropCalendarParser(76005), ['1', '6'])
        self.assertEqual(cropCalendarParser(356008), ['1', '12'])
        self.assertEqual(cropCalendarParser(392000), ['1', '12'])
        self.assertEqual(cropCalendarParser(826000), ['11', '8'])

class DistanceTester(unittest.TestCase):
    
    def setUp(self):
        self.point1 = Point(15, 10)
        point2 = [65, 49]
        point3 = [-4, -19]
        point4 = [110, -25]
        point5 = [-10, 87]
        self.point_list = [point2, point3, point4, point5]

    def test_distance(self):
        self.assertEqual(pointDist(self.point1, self.point_list), [6653.870761714895, 4074.8314834580983, 10612.733565757557, 8268.77623534777])

class PrecipTester(unittest.TestCase):

    def test_coords(self):
        # bring in correct data
        correct = loadPickle('./resources/testing_files/coords.pickle')
        # assert equal
        self.assertEqual(precipFileParser('./resources/precip_data/precip.1950', [4, 9], True, True), correct)

class SHPFileImportTester(unittest.TestCase):

    def test_import(self):
        # get needed objects
        cmd_args = Parameters('./resources/testing_files/shortened.shp', False, None)
        correct = loadPickle('./resources/testing_files/correct_shortened.pickle')
        imported_shp = getShapeFile(cmd_args)
        # check for correct import
        self.assertTrue(imported_shp.equals(correct))

    def test_dropOrigin(self):
        cmd_args = Parameters('./resources/testing_files/origin.shp', False, None)
        gdf = getShapeFile(cmd_args)
        # check for no origin points
        self.assertNotIn(Point(0, 0), gdf['geometry'])


if __name__ == '__main__':
    unittest.main()