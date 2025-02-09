""" 
WEBSCRAPING_PART2
By Sander Bogers
Last changed 20250203

# NOTES #
Central question "if I need to complete my Fantasy football with forwards: 
is it best to choose English or non-English players?"

# CHANGES #
No changes
"""

import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv, find_dotenv

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

#Function for median value of grouped dataframe column
def median(data,column,value):
    """Calculates median of grouped column from dataframe"""
    return data.groupby([column])[value].median()

#Function for mean value of grouped dataframe column
def avg(data,column,value):
    """Calculates average of grouped column from dataframe"""
    return data.groupby([column])[value].mean()

CLEANED_DATA_ROUTE = os.getenv("CLEANED_DATA_ROUTE")

#Retrieve player data from Json file and convert to df
PLAYERDATA_DETAILS = CLEANED_DATA_ROUTE.format("playerData.json")
data_df = pd.read_json(PLAYERDATA_DETAILS)

#Only consider players who've played 30 minutes or more
data_df = data_df.loc[(data_df['Min'] >= 30)]
data_df.reset_index(inplace=True)

conditions = [
    ((data_df['Min'] / data_df['MP']) >= 60),
    ((data_df['Min'] / data_df['MP']) < 60)]
choices = [(data_df['MP'] * 2), (data_df['MP'] * 1)]
data_df['pointsMinPlayed'] = \
np.select(conditions, choices, default=0) #Calculate points from minutes played
data_df['pointsG+A'] = \
(4 * data_df['Gls']) + (3 * data_df['Ast']) #Calcute points from goals/assists
data_df['pointsTotal'] = \
    (4 * data_df['Gls']) + (3 * data_df['Ast'] \
    + data_df['pointsMinPlayed']) #Combined points from minutes played and goals/assists


gbMedian = median(data_df,'ENGlabel','pointsTotal')
gbMedian.to_json(CLEANED_DATA_ROUTE.format("pointsMedianGroup.json", orient='split'))
gbMean = avg(data_df,'ENGlabel','pointsTotal')
gbMean.to_json(CLEANED_DATA_ROUTE.format("pointsMeanGroup.json", orient='split'))

print("The median total points per group is:")
print(gbMedian)
print("*"*10)
print("The mean total points per group is: ")
print(gbMean)

#English players sorted from most to least total points
dfENG = data_df.loc[(data_df['ENGlabel'] == 'ENG')]
dfENG = dfENG.sort_values(by=['pointsTotal'], ascending=False)
dfENG = dfENG.drop(columns=['index'])
dfENG = dfENG.reset_index(drop=True)
#Make new dataset available for data analysis
dfENG.to_json(CLEANED_DATA_ROUTE.format("pointsTotalPlayer_ENG.json",orient='records'))

#Non-English players sorted from most to least total points
dfNonENG = data_df.loc[(data_df['ENGlabel'] != 'ENG')]
dfNonENG = dfNonENG.sort_values(by=['pointsTotal'], ascending=False)
dfNonENG = dfNonENG.drop(columns=['index'])
dfNonENG = dfNonENG.reset_index(drop=True)
#Make new dataset available for data analysis
dfNonENG.to_json(CLEANED_DATA_ROUTE.format("pointsTotalPlayer_NonENG.json",orient='records'))
