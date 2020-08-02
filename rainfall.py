# This script will gather the rainfall data and organize it by percentile
# Caleb Bitting (Colby Class of 2023)
# Written for research for Professor Daniel LaFave at Colby College
#

import statistics
import file_parsers as fp
import pandas as pd
import itertools
import numpy as np
import scipy.stats as stats


class Helper():

    def __init__(self, win_length):
        self.loc = []
        self.beta = []
        self.win_length = win_length

    def extract_attr(self, attr):
        dummy = pd.Series(data=np.nan, index=list(range(self.win_length)))
        loc_series = pd.Series(attr)

        return pd.concat([dummy, loc_series]).reset_index(drop=True)

    def get_stats(self, window):
        alpha, loc, beta = getStats(window)
        self.loc.append(loc)
        self.beta.append(beta)
        return alpha

def expandRow(df_row, helper_object, win_length):
    rain = df_row['Rainfall Totals'].tolist()[0]
    rain = rain.split(',')
    rain = [float(item.strip('][')) for item in rain]
    df_row.drop('Rainfall Totals', axis=1, inplace=True)
    new_df = pd.concat([df_row]*len(rain), ignore_index=True)
    new_df['Rainfall Totals'] = rain

    new_df['Alpha'] = new_df['Rainfall Totals'].rolling(win_length).apply(helper_object.get_stats)
    new_df['Location'] = helper_object.extract_attr(helper_object.loc)
    new_df['Beta'] = helper_object.extract_attr(helper_object.beta)


    return new_df

# formulas taken from https://wiki.analytica.com/index.php?title=Gamma_distribution#CumGamma.28x.2C_alpha.2C_beta.29 and https://www.geeksforgeeks.org/scipy-stats-skew-python/#:~:text=skew(array%2C%20axis%3D0,right%20tail%20of%20the%20distribution.
def getStats(values):
    # target_value = values.pop(len(values.index) - 1)
    # print(target_value)

    avg = statistics.mean(values)
    med = statistics.median(values)
    stdev = statistics.stdev(values)
    skew = (3 * (avg - med))/stdev

    alpha = 4/(skew**2)
    loc = avg - stdev*(alpha**.5)
    beta = stdev**2/(avg-loc)

    return (alpha, loc, beta)
    # return stats.gamma.cdf(target_value, alpha, loc=loc, scale=beta)

def addRolling(df):
    df['Mean'] = df['Rainfall Totals'].rolling(30).mean().shift(1)
    df['Std Dev'] = df['Rainfall Totals'].rolling(30).std().shift(1)

    return df

def main():
    win_length = 30
    helper = Helper(win_length)
    df = pd.read_csv('../pre-processed data/rainfall.csv')
    rows = len(df.index)
    dfs = np.split(df, rows)
    test = expandRow(dfs[0], helper, win_length)
    test.dropna(subset=['Alpha', 'Location', 'Beta'], inplace=True)
    rain = test['Rainfall Totals'].tolist()
    alpha_list = test['Alpha'].tolist()
    loc_list = test['Location'].tolist()
    beta_list = test['Beta'].tolist()
    gammas = [stats.gamma.cdf(r, a, loc=l, scale=b) for r, a, l, b in zip(rain, alpha_list, loc_list, beta_list)]
    print(gammas)

if __name__ == '__main__':
    main()