import forecast_functions as f
import pandas as pd
from datetime import datetime, timedelta

forecast_accuracy = [[0]*len(f.locations) for i in range(len(f.variables))]

for variable_id in range(len(f.variables)):
    for city_id in range(len(f.locations)):
        forecast_accuracy[variable_id][city_id] = f.merge_forecast(f.locations[city_id], f.variables[variable_id])
        # print(combined_forecast_accuracy[variable_id][city_id])

forecast = forecast_accuracy[0][0]
# forecast.set_index('datetime', inplace=True)
# print(forecast)
f.create_chart_by_city(forecast_accuracy)