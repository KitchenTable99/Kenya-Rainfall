# This file will create the appropriate csv file to represent birth data
# Caleb Bitting (Colby Class of 2023)
# Written for research for Professor Daniel LaFave at Colby College
#

import itertools
import numpy as np
import pandas as pd

class Mother():

    master_df = None
    collection_year = 2014

    def __init__(self, id_num):
        self.id_num = id_num
        self.df_subset = Mother.master_df.loc[Mother.master_df['caseid'] == id_num]
        self.dhs_clust = self.df_subset['clusterno'][0]
        self.birth_year = self.df_subset['birthyear'][0]
        self.collected_range = list(range(self.birth_year + 15, Mother.collection_year + 1))
        self.mother_age = [dyear - self.birth_year for dyear in self.collected_range]
        self.gave_birth = self.df_subset['kidbirthyr'].tolist()

    def genDataArray(self):
        final_length = len(self.collected_range)
        clust = list(itertools.repeat(self.dhs_clust, final_length))
        id_num = list(itertools.repeat(self.id_num, final_length))
        kids = [True if year in self.gave_birth else False for year in self.collected_range]
        data = np.array([clust, id_num, self.collected_range, self.mother_age, kids]).T
        print(data)

    def __repr__(self):
        return f'Mother({self.id_num})'

    def __str__(self):
        output = ''
        output += f'id_num = {self.id_num}\n'
        output += f'dhs_clust = {self.dhs_clust}\n'
        output += f'birth year = {self.birth_year}\n'
        output += f'collected_range = {self.collected_range}\n'
        output += f'mother age = {self.mother_age}\n'
        output += f'give birth years = {self.gave_birth}'

        return output

def main():
    input_df = pd.read_csv('./resources/ken_dhs14_raw.csv')
    Mother.master_df = input_df
    tester = Mother('0001006 02')
    tester.genDataArray()

if __name__ == '__main__':
    main()
