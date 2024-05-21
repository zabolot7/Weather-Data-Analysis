import forecast_functions as f

forecast_accuracy = [[0]*len(f.locations) for i in range(len(f.variables))]

for variable_id in range(len(f.variables)):
    for city_id in range(len(f.locations)):
        forecast_accuracy[variable_id][city_id] = f.merge_forecast(f.locations[city_id], f.variables[variable_id])

f.create_chart_by_city(forecast_accuracy)