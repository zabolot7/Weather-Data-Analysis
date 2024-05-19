import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Range1d, Select
from bokeh.palettes import Bokeh6
from bokeh.plotting import figure
from bokeh.io import show

locations = ["Rovaniemi", "Warsaw", "Tripoli", "Kinshasa", "Cape_Town"]
variables = ["temperature_2m", "precipitation", "cloud_cover", "wind_speed_10m", "wind_direction_10m"]

variables_dict = {
    "temperature_2m": 0,
    "precipitation": 1,
    "cloud_cover": 2,
    "wind_speed_10m": 3,
    "wind_direction_10m": 4
}

def calculate_forecast_devs(city, variable):
    actual_filename = "weather_" + city + ".csv"
    forecast_filename = "forecast_" + city + ".csv"

    city_actual_df = pd.read_csv(actual_filename)
    city_forecast_df = pd.read_csv(forecast_filename)

    city_variable_actual_df = city_actual_df.loc[:, ["datetime", variable]]

    forecast_colnames = ["datetime"]
    for day_id in range(8):
        curr_str = variable + "_previous_day" + str(day_id)
        forecast_colnames.append(curr_str)

    city_forecast_df = city_forecast_df.loc[:, forecast_colnames]
    city_variable_df = pd.merge(city_variable_actual_df, city_forecast_df, how="inner", on="datetime")

    city_variable_diffs_df = city_actual_df.loc[:, ["datetime"]]

    for day_id in range(8):
        new_col_name = variable + "_diff_day" + str(day_id) + "_vs_act"
        source_col_name = forecast_colnames[day_id + 1]
        if variable == "wind_direction_10m":
            dir_diff = (city_variable_df.loc[:, variable] - city_variable_df.loc[:, source_col_name]).abs()
            city_variable_diffs_df.loc[:, new_col_name] = np.minimum(dir_diff, 360 - dir_diff)
        else:
            city_variable_diffs_df.loc[:, new_col_name] = (city_variable_df.loc[:, variable] - city_variable_df.loc[:, source_col_name]).abs()

    # print(city_variable_diffs_df.dtypes)
    # print(city_variable_diffs_df.loc[:, ["datetime"]])
    # print(pd.to_datetime(city_variable_diffs_df.loc[:, "datetime"], utc=True))
    # city_variable_diffs_df.loc[:, ["date"]] = pd.to_datetime(city_variable_diffs_df.loc[:, "datetime"], utc=True)
    # print(city_variable_diffs_df.dtypes)

    city_variable_diffs_df.loc[:, ["date"]] = pd.to_datetime(city_variable_diffs_df.loc[:, "datetime"], utc=True).dt.date
    city_variable_diffs_df.drop(["datetime"], axis=1, inplace=True)

    city_variable_diffs_df = city_variable_diffs_df.groupby(["date"]).mean()
    return city_variable_diffs_df

def calculate_city_avgs(variable):
    city_avgs = pd.DataFrame()
    for location in locations:
        current_avgs = calculate_forecast_devs(location, variable).mean()
        city_avgs = pd.concat([city_avgs, current_avgs], axis=1)

    city_avgs.columns = locations

    return city_avgs

def create_chart_forecast_accuracy_over_time(variable, forecast_devs_df):
    title_text = variable + "_forecast_devs_chart"

    plot = figure(width=800, height=400)
    plot.x_range = Range1d(7, 0)
    plot.title.text = title_text

    for city_id in range(len(locations)):
        plot.line([0, 1, 2, 3, 4, 5, 6, 7], forecast_devs_df.loc[:, locations[city_id]], color=Bokeh6[city_id + 1], width=3, legend_label=locations[city_id])

    plot.add_layout(plot.legend[0], 'right')

    plot.xaxis.axis_label = "forecast from _ days before"
    plot.yaxis.axis_label = variable

    plot.legend.click_policy = "mute"

    show(plot)

    #select = Select(title="Option:", value=variables[0], options=variables)
    # select.js_on_change("value", CustomJS(code="""
    #     console.log('select: value=' + this.value, this.toString())
    # """))
    #layout = column(select, plot)
    # show(layout)

    #curdoc().add_root(layout)

def create_full_chart(combined_forecast_accuracy):
    variable_select = Select(title="Option:", value=variables[0], options=variables)

    # title_text = variable + "_forecast_devs_chart"

    plot = figure(width=800, height=400)
    plot.x_range = Range1d(7, 0)
    # plot.title.text = title_text

    forecast_devs_df = combined_forecast_accuracy[0]
    variable = variables[0]

    for city_id in range(len(locations)):
        plot.line([0, 1, 2, 3, 4, 5, 6, 7], forecast_devs_df.loc[:, locations[city_id]], color=Bokeh6[city_id + 1], width=3, legend_label=locations[city_id])

    plot.add_layout(plot.legend[0], 'right')

    plot.xaxis.axis_label = "forecast from _ days before"
    plot.yaxis.axis_label = variable

    plot.legend.click_policy = "mute"

    def update_plot(attrname, old, new):
        variable = variable_select.value
        plot.title.text = "Forecast accuracy of" + variable
        forecast_devs_df = combined_forecast_accuracy[variables_dict[variable_select.value]]

    variable_select.on_change('value', update_plot)

    # select.js_on_change("value", CustomJS(code="""
    #     console.log('select: value=' + this.value, this.toString())
    # """))

    curdoc().add_root(column(variable_select, plot))
    # curdoc().title = "forecast_accuracy_full_chart"


def create_full_chart_1(combined_forecast_accuracy):

    plot = figure(width=800, height=400)
    plot.x_range = Range1d(7, 0)

    first_variable = variables[0]
    forecast_devs_df = combined_forecast_accuracy[first_variable]
    title_text = "Forecast accuracy of " + first_variable
    plot.title.text = title_text

    lines = [0]*len(locations)
    for city_id in range(len(locations)):
        lines[city_id] = plot.line([0, 1, 2, 3, 4, 5, 6, 7], forecast_devs_df.loc[:, locations[city_id]], color=Bokeh6[city_id + 1], width=3, legend_label=locations[city_id])
    # plot.add_layout(plot.legend, 'right')

    plot.xaxis.axis_label = "forecast from _ days before"
    plot.yaxis.axis_label = first_variable

    plot.legend.click_policy = "mute"

    def update_plot(attr, old, new):
        first_variable = variable_select.value
        plot.title.text = "Forecast accuracy of " + first_variable
        forecast_devs_df = combined_forecast_accuracy[variable_select.value]
        for city_id in range(len(locations)):
            plot.renderers.remove(lines[city_id])
            lines[city_id] = plot.line([0, 1, 2, 3, 4, 5, 6, 7], forecast_devs_df.loc[:, locations[city_id]], color=Bokeh6[city_id + 1], width=3, legend_label=locations[city_id])

    variable_select = Select(title="Option:", value=variables[0], options=variables)
    variable_select.on_change('value', update_plot)

    curdoc().add_root(column(variable_select, plot))
    curdoc().title = "forecast_accuracy_full_chart"

def main():
    combined_forecast_accuracy = dict()

    for variable in variables:
        combined_forecast_accuracy[variable] = calculate_city_avgs(variable)
        # if variable == "temperature_2m":
        #     create_chart_forecast_accuracy_over_time(variable, calculate_city_avgs(variable))

    create_full_chart_1(combined_forecast_accuracy)

if __name__ == "__main__":
    main()

## main

combined_forecast_accuracy = dict()

for variable in variables:
    combined_forecast_accuracy[variable] = calculate_city_avgs(variable)

create_full_chart_1(combined_forecast_accuracy)