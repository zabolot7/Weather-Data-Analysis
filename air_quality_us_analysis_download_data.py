import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry


def download_aq_csv():
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": [40.7143, 34.0522, 41.85, 32.7831, 33.4484, 37.7749, 45.5234, 36.1659],
        "longitude": [-74.006, -118.2437, -87.65, -96.8067, -112.074, -122.4194, -122.6762, -86.7844],
        "hourly": ["pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide"],
        "start_date": "2023-01-01",
        "end_date": "2023-12-31"
    }
    responses = openmeteo.weather_api(url, params=params)

    locations = ["New York", "Los Angeles", "Chicago", "Dallas", "Phoenix", "San Francisco", "Portland", "Nashville"]

    for location_id in range(len(responses)):
        response = responses[location_id]

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

        hourly_dataframe = pd.DataFrame(data=hourly_data)

        current_file_name = "air_quality_us_" + locations[location_id] + ".csv"
        hourly_dataframe.to_csv(current_file_name)


def main():
    download_aq_csv()


if __name__ == '__main__':
    main()
