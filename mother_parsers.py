# This file will create the appropriate csv file to represent birth data
# Caleb Bitting (Colby Class of 2023)
# Written for research for Professor Daniel LaFave at Colby College
#

import argparse
import itertools
import numpy as np
import pandas as pd
from tqdm import tqdm as progress

class Mother():

    master_df = None
    collection_year = None

    def __init__(self, id_num):
        self.id_num = id_num
        self.df_subset = Mother.master_df.loc[Mother.master_df['idhspid'] == id_num]                 # the relevant rows of the df
        self.dhsid = self.df_subset['dhsid'].iloc[0]
        self.birth_year = self.df_subset['birthyear'].iloc[0]
        self.collected_range = list(range(self.birth_year + 14, Mother.collection_year + 1))        # over what years was this mother surveyed
        self.mother_age = [dyear - self.birth_year for dyear in self.collected_range]               # how old was she
        self.gave_birth = self.df_subset['kidbirthyr'].tolist()                                     # what years did she give birth
        self.kids = [True if year in self.gave_birth else False for year in self.collected_range]   # make a list of booleans for births

    def genDataArray(self):
        '''Generate an array containing all the information pertaining to this mother.
        
        Returns:
            np.array: DHSCLUST, Mother ID, Year, Age, Birth in an array. Shape is len(collected_range) by 5
        '''
        # figure out how long
        final_length = len(self.collected_range)
        # create the constant lists
        clust = list(itertools.repeat(self.dhsid, final_length))
        id_num = list(itertools.repeat(self.id_num, final_length))
        # create an array and reflect it with np.array.T
        data = np.array([clust, id_num, self.collected_range, self.mother_age, self.kids]).T
        
        return data

    def genHazardArray(self):
        # get the event time and censorship status
        try:
            event_index = self.kids.index(True)
            event_time = event_index + 1
            event_occured = 1
            event_year = self.collected_range[event_index] - 1
        except ValueError:
            event_time = len(self.kids)
            event_occured = 0
            event_year = Mother.collection_year - 1

        # create array
        data = np.array([self.id_num, event_time, event_occured, self.dhsid, event_year])

        return data

    def __repr__(self):
        return f'Mother({self.id_num})'

    def __str__(self):
        output = ''
        output += f'id_num = {self.id_num}\n'
        output += f'dhsid = {self.dhsid}\n'
        output += f'birth year = {self.birth_year}\n'
        output += f'collected_range = {self.collected_range}\n'
        output += f'mother age = {self.mother_age}\n'
        output += f'give birth years = {self.gave_birth}'

        return output

def commandLineParser():
    '''This function parses the command line arguments
    
    Returns:
        argparse.namespace: an argparse namespace representing the command line arguments
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('input_csv', type=str, help='the name of the csv containing the DHS survey data.')
    parser.add_argument('--output_csv', type=str, default='mother_data.csv', help='what to call the output csv file.')
    parser.add_argument('--hazard_regressions', action='store_true', help='whether or not the output will be used to run hazard regressions.')
    args = parser.parse_args()

    return args

def test():
    # get command-line arguments
    cmd_args = commandLineParser()
    # assign Class variable to the correct DataFrame
    input_df = pd.read_csv(cmd_args.input_csv)
    survey_year = input_df['year'].iloc[0]
    Mother.collection_year = survey_year
    Mother.master_df = input_df

def getHazardDataFrame(df):
    survey_year = df['year'].iloc[0]
    Mother.collection_year = survey_year
    Mother.master_df = df
    # make a list of all unique mother id
    id_num_list = df['idhspid'].tolist()
    id_num_list = list(dict.fromkeys(id_num_list))
    # create a Mother object for each id
    mother_list = [Mother(num) for num in progress(id_num_list, desc='Creating mother objects')]
    # create an array containing all relevant data
    mother_arrays = [mother.genHazardArray() for mother in mother_list]
    data = np.column_stack(mother_arrays).T
    out_df = pd.DataFrame(data=data, columns=['IDHSPID', 'Event Time', 'Event Occured', 'DHSID', 'Rainfall Data Year'])
    
    return out_df

def main():
    # get command-line arguments
    cmd_args = commandLineParser()
    # assign Class variable to the correct DataFrame
    input_df = pd.read_csv(cmd_args.input_csv)
    if cmd_args.hazard_regressions:
        df = getHazardDataFrame(input_df)
    else:
        survey_year = input_df['year'].iloc[0]
        Mother.collection_year = survey_year
        Mother.master_df = input_df
        # make a list of all unique mother id
        id_num_list = input_df['idhspid'].tolist()
        id_num_list = list(dict.fromkeys(id_num_list))
        # create a Mother object for each id
        mother_list = [Mother(num) for num in progress(id_num_list, desc='Creating mother objects')]
        # create an array containing all relevant data
        mother_arrays = [mother.genDataArray() for mother in mother_list]
        data = np.concatenate(mother_arrays)
        df = pd.DataFrame(data=data, columns=['DHSID', 'IDHSPID', 'Year', 'Mother\'s Age', 'Baby?'])
    # make a new DataFrame and export as csv
    df.to_csv(cmd_args.output_csv, index=False)

if __name__ == '__main__':
    main()
