""" 
WEBSCRAPING_PART1 
By Sander Bogers
Last changed 20250203

# NOTES #
Central question "if I need to complete my Fantasy football with forwards: 
is it best to choose English or non-English players?"

# CHANGES #
No changes
"""

import sys
import os
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import numpy as np
from dotenv import find_dotenv, load_dotenv

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

#EXTRACT
URL = r"https://fbref.com/en/comps/9/stats/Premier-League-Stats" #Link to get Premier League data

try:
    response = requests.get(URL, timeout=10) #Test connection
    if response.status_code == 200:
        print("Successful connection")
    elif response.status_code == 404:
        sys.exit("The connection couldn't be established, please check")
except requests.exceptions.Timeout:
    print("Timed out")

driver = webdriver.Chrome() #Set up driver
driver.get(URL)
driver.implicitly_wait(10) #Wait for loading

playerTable = driver.find_element(By.ID, "div_stats_standard").get_attribute("outerHTML")
df = pd.read_html(playerTable)[0] #Retrieve first table found
driver.quit() #Safely end driver session

#TRANSFORM (make it workable for loading)
columns = df.columns.droplevel() #Drop multi index
df = df.reset_index(drop=True) #Reset index
df.columns = columns #Reset column names
df = df.fillna(0) #Fill any blank space

df['Age'] = df['Age'].str[:2]
df['Position_2'] = df['Pos'].str[3:]
df['Position'] = df['Pos'].str[:2]
df['Nation'] = df['Nation'].str.split(' ').str.get(1)

conditions = [
    (df['Nation'] == 'ENG'),
    (df['Nation'] != 'ENG')]
choices = ['ENG', 'nonENG'] #Add column to later group by English and non-English players
df['ENGlabel'] = np.select(conditions, choices, default='ENG')

df['Rk'] = df['ENGlabel'] #Rk column will be dropped regardless, so switched with ENGlabel
df.rename(columns={'Rk':'ENGlabel'}, inplace=True)

df = df.drop(columns=['Pos','Matches']) #Drop columns without purpose
df = df.drop(df[df['Player'] == 'Player'].index) #Drop every row serving as 'subheader'
df['Position'] = df['Position'].replace \
({'MF': 'Midfielder', 'DF': 'Defender', 'FW': 'Forward', 'GK': 'Goalkeeper'}) #Relabel position
df['Position_2'] = df['Position_2'].replace \
({'MF': 'Midfielder', 'DF': 'Defender','FW': 'Forward', 'GK': 'Goalkeeper'}) #Relabel position

#Only select players with their assigned position forward on first or second place
df = df.loc[(df['Position'] == 'Forward') | (df['Position_2'] == 'Forward')]

# Slicing columns in data frame
df = df.iloc[:, 0:15]

df.reset_index(inplace=True, drop=True)
print(df.head()) #Print first 10 rows as test to get a feeling of the data

#LOAD
CLEANED_DATA_ROUTE = os.getenv("CLEANED_DATA_ROUTE")
df.to_json(CLEANED_DATA_ROUTE.format("playerData.json"), orient='records')
