import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

def download_usa_data(openmeteo):
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": [33.57, 40.01, 29.46, 32.81, 32.79],
        "longitude": [112.09, 75.13, 98.52, 117.14, 96.77],
        "hourly": ["pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide"],
        "start_date": "2023-01-01",
        "end_date": "2023-12-31"
    }
    responses = openmeteo.weather_api(url, params=params)

    locations = ["Phoenix", "Philadelphia", "San_Antonio", "San_Diego", "Dallas"]

    for location_id in range(len(responses)):
        response = responses[location_id]
        # print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
        # print(f"Elevation {response.Elevation()} m asl")
        # print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
        # print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_pm10 = hourly.Variables(0).ValuesAsNumpy()
        hourly_pm2_5 = hourly.Variables(1).ValuesAsNumpy()
        hourly_carbon_monoxide = hourly.Variables(2).ValuesAsNumpy()
        hourly_nitrogen_dioxide = hourly.Variables(3).ValuesAsNumpy()
        hourly_sulphur_dioxide = hourly.Variables(4).ValuesAsNumpy()

        hourly_data = {"date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )}
        hourly_data["pm10"] = hourly_pm10
        hourly_data["pm2_5"] = hourly_pm2_5
        hourly_data["carbon_monoxide"] = hourly_carbon_monoxide
        hourly_data["nitrogen_dioxide"] = hourly_nitrogen_dioxide
        hourly_data["sulphur_dioxide"] = hourly_sulphur_dioxide

        hourly_dataframe = pd.DataFrame(data = hourly_data)

        current_file_name = "pollution_" + locations[location_id] + ".csv"
        hourly_dataframe.to_csv(current_file_name)

def download_europe_data(openmeteo):
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": [47.50, 41.40, 48.14, 50.09, 45.46],
        "longitude": [19.08, 2.17, 11.57, 14.46, 9.18],
        "hourly": ["pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide"],
        "start_date": "2023-01-01",
        "end_date": "2023-12-31"
    }
    responses = openmeteo.weather_api(url, params=params)

    locations = ["Budapest", "Barcelona", "Munich", "Prague", "Milan"]

    for location_id in range(len(responses)):
        response = responses[location_id]
        # print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
        # print(f"Elevation {response.Elevation()} m asl")
        # print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
        # print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_pm10 = hourly.Variables(0).ValuesAsNumpy()
        hourly_pm2_5 = hourly.Variables(1).ValuesAsNumpy()
        hourly_carbon_monoxide = hourly.Variables(2).ValuesAsNumpy()
        hourly_nitrogen_dioxide = hourly.Variables(3).ValuesAsNumpy()
        hourly_sulphur_dioxide = hourly.Variables(4).ValuesAsNumpy()

        hourly_data = {"date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )}
        hourly_data["pm10"] = hourly_pm10
        hourly_data["pm2_5"] = hourly_pm2_5
        hourly_data["carbon_monoxide"] = hourly_carbon_monoxide
        hourly_data["nitrogen_dioxide"] = hourly_nitrogen_dioxide
        hourly_data["sulphur_dioxide"] = hourly_sulphur_dioxide

        hourly_dataframe = pd.DataFrame(data = hourly_data)

        current_file_name = "pollution_" + locations[location_id] + ".csv"
        hourly_dataframe.to_csv(current_file_name)

def main():
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    download_usa_data(openmeteo)
    download_europe_data(openmeteo)

if __name__ == "__main__":
    main()