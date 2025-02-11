"""
Get today's weather using OPENWEATHERMAP.ORG
By SB
Last changed 20250211

#NOTES

#CHANGES

"""

import os
import requests
from dotenv import load_dotenv, find_dotenv

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

WEATHER_KEY = os.getenv("WEATHER_APIKEY")

# City and base url
CITY = "Amsterdam, NL"
url = f'http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_KEY}&units=metric'

res = requests.get(url, timeout=10)
data = res.json()

humidity = data['main']['humidity']
pressure = data['main']['pressure']
wind = data['wind']['speed']
description = data['weather'][0]['description']
temp = data['main']['temp']

# Today's weather information
print(f"Today's weather for {CITY} is: ")
print('Temperature:',temp,'°C')
print('Wind:',wind)
print('Pressure: ',pressure)
print('Humidity: ',humidity)
print('Description:',description)
