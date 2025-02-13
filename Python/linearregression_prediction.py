"""
Predict next hour's temperature using open data from KNMI (De Bilt) from last 10 years
By SB
Last changed 20250213

#NOTES
# Historial period goes from 20150211 up to and including 20250211
# Source: https://www.daggegevens.knmi.nl/klimatologie/uurgegevens

#CHANGES

"""

import os
import calendar
import datetime
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from dotenv import load_dotenv, find_dotenv
from todaysweather_api import temp, CITY

now = datetime.datetime.now()
next_hour = now.hour + 1
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

WEATHER_DATA = os.getenv("WEATHER_DATA")
CLEANED_DATA_ROUTE = os.getenv("CLEANED_DATA_ROUTE")
RAW_DATA_ROUTE = os.getenv("RAW_DATA_ROUTE")

def calculate_temperature():
    """Calculation of expected temperature"""
    df_input = pd.read_json(RAW_DATA_ROUTE.format(
        f"KNMI_HM\\KNMI_WeatherData_HM{next_hour}-{now.month}.json"
        ))

    x = np.array(df_input[['Temp']])
    y = np.array(df_input[['TempD']])
    model = LinearRegression().fit(x,y)

    delta_temp = model.predict(np.array([[temp]], dtype=object))
    delta_temp = delta_temp[0][0]
    temperature = round((temp + delta_temp),2)
    return print(f"A temperature of {temperature}(C) is expected "
                 f"during {next_hour}h in {calendar.month_name[now.month]} for {CITY}.")


df = pd.read_json(WEATHER_DATA)
df['Temp'] = df['T'] / 10
df['month'] = df['date'].dt.month
df = df.dropna()

df['Temp1'] = df['Temp']
df['Temp1'] = df['Temp1'].shift(periods=-1)
df['TempD'] = df['Temp1'] - df['Temp']
df = df.drop(['Temp1'], axis=1)

for h in range(24):
    df_h = df.loc[df['hour'] == h + 1]
    df_h.to_json(RAW_DATA_ROUTE.format(f"KNMI_H\\KNMI_WeatherData_H{h+1}.json"),
                 orient='records', index=False)

for h in range(24):
    df = pd.read_json(RAW_DATA_ROUTE.format(f"KNMI_H\\KNMI_WeatherData_H{h+1}.json"))
    for m in range(12):
        df_hm = df.loc[df['month'] == m + 1]
        df_hm.to_json(RAW_DATA_ROUTE.format(f"KNMI_HM\\KNMI_WeatherData_HM{h+1}-{m+1}.json"),
                      orient='records', index=False)

calculate_temperature()
