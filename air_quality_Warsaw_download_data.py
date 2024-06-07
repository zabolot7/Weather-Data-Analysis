import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

url = "https://air-quality-api.open-meteo.com/v1/air-quality"
params = {
	"latitude": 52.351,
	"longitude": 20.977,
	"hourly": "pm2_5",
	"start_date": "2023-01-01",
	"end_date": "2023-12-31"
}
responses = openmeteo.weather_api(url, params=params)

response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

hourly = response.Hourly()
hourly_pm2_5 = hourly.Variables(0).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}
hourly_data["pm2_5"] = hourly_pm2_5

hourly_dataframe = pd.DataFrame(data = hourly_data)
current_file_name = "air_quality_Warsaw.csv"
hourly_dataframe.to_csv(current_file_name)
