import forecast_functions as f

combined_forecast_accuracy = dict()

for variable in f.variables:
    combined_forecast_accuracy[variable] = f.calculate_city_avgs(variable)

f.create_full_chart(combined_forecast_accuracy)