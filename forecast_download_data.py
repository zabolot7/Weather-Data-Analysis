import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry

def download_forecasts_csv(openmeteo):
    url = "https://previous-runs-api.open-meteo.com/v1/forecast"
    params = {
        "latitude": [66.512, 52.351, 32.941, -4.372, -33.926],
        "longitude": [25.706, 20.977, 13.082, 15.301, 18.421],
        "hourly": ["temperature_2m", "temperature_2m_previous_day1", "temperature_2m_previous_day2",
                   "temperature_2m_previous_day3", "temperature_2m_previous_day4", "temperature_2m_previous_day5",
                   "temperature_2m_previous_day6", "temperature_2m_previous_day7", "precipitation",
                   "precipitation_previous_day1", "precipitation_previous_day2", "precipitation_previous_day3",
                   "precipitation_previous_day4", "precipitation_previous_day5", "precipitation_previous_day6",
                   "precipitation_previous_day7", "cloud_cover", "cloud_cover_previous_day1",
                   "cloud_cover_previous_day2", "cloud_cover_previous_day3", "cloud_cover_previous_day4",
                   "cloud_cover_previous_day5", "cloud_cover_previous_day6", "cloud_cover_previous_day7",
                   "wind_speed_10m", "wind_speed_10m_previous_day1", "wind_speed_10m_previous_day2",
                   "wind_speed_10m_previous_day3", "wind_speed_10m_previous_day4", "wind_speed_10m_previous_day5",
                   "wind_speed_10m_previous_day6", "wind_speed_10m_previous_day7", "wind_direction_10m",
                   "wind_direction_10m_previous_day1", "wind_direction_10m_previous_day2",
                   "wind_direction_10m_previous_day3", "wind_direction_10m_previous_day4",
                   "wind_direction_10m_previous_day5", "wind_direction_10m_previous_day6",
                   "wind_direction_10m_previous_day7"],
        #"timezone": "auto",
        "start_date": "2024-04-01",
        "end_date": "2024-04-30",
        "models": "ecmwf_ifs04"
    }
    responses = openmeteo.weather_api(url, params=params)

    locations = ["Rovaniemi", "Warsaw", "Tripoli", "Kinshasa", "Cape_Town"]

    for location_id in range(len(responses)):
        response = responses[location_id]
#        print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
#        print(f"Elevation {response.Elevation()} m asl")
#        print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
#        print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_temperature_2m_previous_day1 = hourly.Variables(1).ValuesAsNumpy()
        hourly_temperature_2m_previous_day2 = hourly.Variables(2).ValuesAsNumpy()
        hourly_temperature_2m_previous_day3 = hourly.Variables(3).ValuesAsNumpy()
        hourly_temperature_2m_previous_day4 = hourly.Variables(4).ValuesAsNumpy()
        hourly_temperature_2m_previous_day5 = hourly.Variables(5).ValuesAsNumpy()
        hourly_temperature_2m_previous_day6 = hourly.Variables(6).ValuesAsNumpy()
        hourly_temperature_2m_previous_day7 = hourly.Variables(7).ValuesAsNumpy()
        hourly_precipitation = hourly.Variables(8).ValuesAsNumpy()
        hourly_precipitation_previous_day1 = hourly.Variables(9).ValuesAsNumpy()
        hourly_precipitation_previous_day2 = hourly.Variables(10).ValuesAsNumpy()
        hourly_precipitation_previous_day3 = hourly.Variables(11).ValuesAsNumpy()
        hourly_precipitation_previous_day4 = hourly.Variables(12).ValuesAsNumpy()
        hourly_precipitation_previous_day5 = hourly.Variables(13).ValuesAsNumpy()
        hourly_precipitation_previous_day6 = hourly.Variables(14).ValuesAsNumpy()
        hourly_precipitation_previous_day7 = hourly.Variables(15).ValuesAsNumpy()
        hourly_cloud_cover = hourly.Variables(16).ValuesAsNumpy()
        hourly_cloud_cover_previous_day1 = hourly.Variables(17).ValuesAsNumpy()
        hourly_cloud_cover_previous_day2 = hourly.Variables(18).ValuesAsNumpy()
        hourly_cloud_cover_previous_day3 = hourly.Variables(19).ValuesAsNumpy()
        hourly_cloud_cover_previous_day4 = hourly.Variables(20).ValuesAsNumpy()
        hourly_cloud_cover_previous_day5 = hourly.Variables(21).ValuesAsNumpy()
        hourly_cloud_cover_previous_day6 = hourly.Variables(22).ValuesAsNumpy()
        hourly_cloud_cover_previous_day7 = hourly.Variables(23).ValuesAsNumpy()
        hourly_wind_speed_10m = hourly.Variables(24).ValuesAsNumpy()
        hourly_wind_speed_10m_previous_day1 = hourly.Variables(25).ValuesAsNumpy()
        hourly_wind_speed_10m_previous_day2 = hourly.Variables(26).ValuesAsNumpy()
        hourly_wind_speed_10m_previous_day3 = hourly.Variables(27).ValuesAsNumpy()
        hourly_wind_speed_10m_previous_day4 = hourly.Variables(28).ValuesAsNumpy()
        hourly_wind_speed_10m_previous_day5 = hourly.Variables(29).ValuesAsNumpy()
        hourly_wind_speed_10m_previous_day6 = hourly.Variables(30).ValuesAsNumpy()
        hourly_wind_speed_10m_previous_day7 = hourly.Variables(31).ValuesAsNumpy()
        hourly_wind_direction_10m = hourly.Variables(32).ValuesAsNumpy()
        hourly_wind_direction_10m_previous_day1 = hourly.Variables(33).ValuesAsNumpy()
        hourly_wind_direction_10m_previous_day2 = hourly.Variables(34).ValuesAsNumpy()
        hourly_wind_direction_10m_previous_day3 = hourly.Variables(35).ValuesAsNumpy()
        hourly_wind_direction_10m_previous_day4 = hourly.Variables(36).ValuesAsNumpy()
        hourly_wind_direction_10m_previous_day5 = hourly.Variables(37).ValuesAsNumpy()
        hourly_wind_direction_10m_previous_day6 = hourly.Variables(38).ValuesAsNumpy()
        hourly_wind_direction_10m_previous_day7 = hourly.Variables(39).ValuesAsNumpy()

        hourly_data = {"datetime": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )}
        hourly_data["temperature_2m_previous_day0"] = hourly_temperature_2m
        hourly_data["temperature_2m_previous_day1"] = hourly_temperature_2m_previous_day1
        hourly_data["temperature_2m_previous_day2"] = hourly_temperature_2m_previous_day2
        hourly_data["temperature_2m_previous_day3"] = hourly_temperature_2m_previous_day3
        hourly_data["temperature_2m_previous_day4"] = hourly_temperature_2m_previous_day4
        hourly_data["temperature_2m_previous_day5"] = hourly_temperature_2m_previous_day5
        hourly_data["temperature_2m_previous_day6"] = hourly_temperature_2m_previous_day6
        hourly_data["temperature_2m_previous_day7"] = hourly_temperature_2m_previous_day7
        hourly_data["precipitation_previous_day0"] = hourly_precipitation
        hourly_data["precipitation_previous_day1"] = hourly_precipitation_previous_day1
        hourly_data["precipitation_previous_day2"] = hourly_precipitation_previous_day2
        hourly_data["precipitation_previous_day3"] = hourly_precipitation_previous_day3
        hourly_data["precipitation_previous_day4"] = hourly_precipitation_previous_day4
        hourly_data["precipitation_previous_day5"] = hourly_precipitation_previous_day5
        hourly_data["precipitation_previous_day6"] = hourly_precipitation_previous_day6
        hourly_data["precipitation_previous_day7"] = hourly_precipitation_previous_day7
        hourly_data["cloud_cover_previous_day0"] = hourly_cloud_cover
        hourly_data["cloud_cover_previous_day1"] = hourly_cloud_cover_previous_day1
        hourly_data["cloud_cover_previous_day2"] = hourly_cloud_cover_previous_day2
        hourly_data["cloud_cover_previous_day3"] = hourly_cloud_cover_previous_day3
        hourly_data["cloud_cover_previous_day4"] = hourly_cloud_cover_previous_day4
        hourly_data["cloud_cover_previous_day5"] = hourly_cloud_cover_previous_day5
        hourly_data["cloud_cover_previous_day6"] = hourly_cloud_cover_previous_day6
        hourly_data["cloud_cover_previous_day7"] = hourly_cloud_cover_previous_day7
        hourly_data["wind_speed_10m_previous_day0"] = hourly_wind_speed_10m
        hourly_data["wind_speed_10m_previous_day1"] = hourly_wind_speed_10m_previous_day1
        hourly_data["wind_speed_10m_previous_day2"] = hourly_wind_speed_10m_previous_day2
        hourly_data["wind_speed_10m_previous_day3"] = hourly_wind_speed_10m_previous_day3
        hourly_data["wind_speed_10m_previous_day4"] = hourly_wind_speed_10m_previous_day4
        hourly_data["wind_speed_10m_previous_day5"] = hourly_wind_speed_10m_previous_day5
        hourly_data["wind_speed_10m_previous_day6"] = hourly_wind_speed_10m_previous_day6
        hourly_data["wind_speed_10m_previous_day7"] = hourly_wind_speed_10m_previous_day7
        hourly_data["wind_direction_10m_previous_day0"] = hourly_wind_direction_10m
        hourly_data["wind_direction_10m_previous_day1"] = hourly_wind_direction_10m_previous_day1
        hourly_data["wind_direction_10m_previous_day2"] = hourly_wind_direction_10m_previous_day2
        hourly_data["wind_direction_10m_previous_day3"] = hourly_wind_direction_10m_previous_day3
        hourly_data["wind_direction_10m_previous_day4"] = hourly_wind_direction_10m_previous_day4
        hourly_data["wind_direction_10m_previous_day5"] = hourly_wind_direction_10m_previous_day5
        hourly_data["wind_direction_10m_previous_day6"] = hourly_wind_direction_10m_previous_day6
        hourly_data["wind_direction_10m_previous_day7"] = hourly_wind_direction_10m_previous_day7

        hourly_dataframe = pd.DataFrame(data=hourly_data)
        # print(hourly_dataframe)

        current_file_name = "forecast_" + locations[location_id] + ".csv"
        # print(current_file_name)
        hourly_dataframe.to_csv(current_file_name)

def download_weather_csv(openmeteo):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": [66.512, 52.351, 32.941, -4.372, -33.926],
        "longitude": [25.706, 20.977, 13.082, 15.301, 18.421],
        "start_date": "2024-04-01",
        "end_date": "2024-04-30",
        "hourly": ["temperature_2m", "precipitation", "cloud_cover", "wind_speed_10m", "wind_direction_10m"],
        "models": "ecmwf_ifs"
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    locations = ["Rovaniemi", "Warsaw", "Tripoli", "Kinshasa", "Cape_Town"]

    for location_id in range(len(responses)):
        response = responses[location_id]

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_precipitation = hourly.Variables(1).ValuesAsNumpy()
        hourly_cloud_cover = hourly.Variables(2).ValuesAsNumpy()
        hourly_wind_speed_10m = hourly.Variables(3).ValuesAsNumpy()
        hourly_wind_direction_10m = hourly.Variables(4).ValuesAsNumpy()

        hourly_data = {"datetime": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )}
        hourly_data["temperature_2m"] = hourly_temperature_2m.round(2)
        hourly_data["precipitation"] = hourly_precipitation
        hourly_data["cloud_cover"] = hourly_cloud_cover
        hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
        hourly_data["wind_direction_10m"] = hourly_wind_direction_10m

        hourly_dataframe = pd.DataFrame(data=hourly_data)

        current_file_name = "weather_" + locations[location_id] + ".csv"
        hourly_dataframe.to_csv(current_file_name)

def main():
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    download_forecasts_csv(openmeteo)
    download_weather_csv(openmeteo)

if __name__ == '__main__':
    main()