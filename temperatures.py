import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

import json
from datetime import datetime

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 41.75,
	"longitude": 2.1167,
	"hourly": "temperature_2m",
	"forecast_days": 1,
}
responses = openmeteo.weather_api(url, params = params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

hourly_data = {
	"date": pd.date_range(
		start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
		end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
		freq = pd.Timedelta(seconds = hourly.Interval()),
		inclusive = "left"
	)
}

hourly_data["temperature_2m"] = hourly_temperature_2m

hourly_dataframe = pd.DataFrame(data = hourly_data)

maxima = hourly_dataframe["temperature_2m"].max()
minima = hourly_dataframe["temperature_2m"].min()
mitjana = hourly_dataframe["temperature_2m"].sum() / len(hourly_dataframe["temperature_2m"])

dades = {"Temperatura maxima":round(float(maxima), 2), "Temperatura minima":round(float(minima), 2), "Temperatura mitjana":round(float(mitjana), 2)}

data_actual = datetime.now().strftime("%Y%m%d")
nom_fitxer = f"temperatures_{data_actual}.json"

with open(nom_fitxer, "w") as f:
    json.dump(dades, f, indent=4)