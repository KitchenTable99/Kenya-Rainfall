# unittest file for file_parsers

import pickle
import unittest
from shapely.geometry import Point
from file_parsers import cropCalendarParser
from file_parsers import pointDist
from file_parsers import getShapeFile

class Parameters():

    def __init__(self, file_path, testing):
        self.shapefile_path = file_path
        self.testing = testing

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

class SHPFileImportTester(unittest.TestCase):

    def test_import(self):
        # get needed objects
        cmd_args = Parameters('./resources/testing_files/shortened.shp', False)
        with open('./resources/testing_files/correct_shortened.pickle', 'rb') as fp:
            correct = pickle.load(fp)
        imported_shp = getShapeFile(cmd_args)
        # check for correct import
        self.assertTrue(imported_shp.equals(correct))

    def test_dropOrigin(self):
        with open('./resources/testing_files/correct_origin.pickle', 'rb') as fp:
            correct = pickle.load(fp)
        # check for no origin points
        self.assertNotIn(Point(0, 0), correct['geometry'])


if __name__ == '__main__':
    unittest.main()