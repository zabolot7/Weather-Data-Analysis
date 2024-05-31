import numpy as np
import pandas as pd

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import Range1d, Select, DateRangeSlider, DatetimeTickFormatter, Legend, HoverTool
from bokeh.palettes import Bokeh6, Blues9
from bokeh.plotting import figure
from bokeh.io import show

locations = ["Rovaniemi", "Warsaw", "Tripoli", "Kinshasa", "Cape_Town"]
variables = ["temperature_2m", "precipitation", "cloud_cover", "wind_speed_10m", "wind_direction_10m"]
variables_with_unit = ["temperature [°C]", "precipitation [mm]", "cloud_cover [%]", "wind_speed [km/h]", "wind_direction_10m [°]"]
units = {
    "temperature_2m": "°C",
    "precipitation": "mm",
    "cloud_cover": "%",
    "wind_speed_10m": "km/h",
    "wind_direction_10m": "°"
}

locations_dict = {
    "Rovaniemi": 0,
    "Warsaw": 1,
    "Tripoli": 2,
    "Kinshasa": 3,
    "Cape_Town": 4
}

variables_dict = {
    "temperature_2m": 0,
    "precipitation": 1,
    "cloud_cover": 2,
    "wind_speed_10m": 3,
    "wind_direction_10m": 4
}


def merge_forecast(city, variable):
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

    return city_variable_df


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


# Tej funkcji nie używamy
def create_chart_forecast_accuracy_over_time(variable, forecast_devs_df):
    title_text = variable + "_forecast_devs_chart"

    plot = figure(width=800, height=400)
    plot.x_range = Range1d(7, 0)
    plot.title.text = title_text

    for city_id in range(len(locations)):
        plot.line([0, 1, 2, 3, 4, 5, 6, 7], forecast_devs_df.loc[:, locations[city_id]],
                  color=Bokeh6[city_id + 1], width=3, legend_label=locations[city_id])

    plot.add_layout(plot.legend[0], 'right')

    plot.xaxis.axis_label = "forecast from _ days before"
    plot.yaxis.axis_label = variable

    plot.legend.click_policy = "mute"

    show(plot)


def create_full_chart(combined_forecast_accuracy):

    plot = figure(width=800, height=400, toolbar_location=None)
    plot.x_range = Range1d(7, 0)

    first_variable = variables[0]
    forecast_devs_df = combined_forecast_accuracy[first_variable]
    title_text = "Forecast accuracy of " + first_variable
    plot.title.text = title_text

    lines = [0]*len(locations)
    items = []
    for city_id in range(len(locations)):
        lines[city_id] = plot.line([0, 1, 2, 3, 4, 5, 6, 7], forecast_devs_df.loc[:, locations[city_id]], color=Bokeh6[city_id + 1], width=3)
        items.append((locations[city_id], [lines[city_id]]))
        hover = HoverTool(tooltips=[
            (locations[city_id], f"@y {units[first_variable]}, @x days before")
        ], renderers=[lines[city_id]])
        plot.add_tools(hover)
    legend = Legend(items=items, location=(10, 196))
    plot.add_layout(legend, 'right')

    plot.xaxis.axis_label = "forecast from _ days before"
    plot.yaxis.axis_label = variables_with_unit[0]

    plot.legend.click_policy = "mute"

    def update_plot(attr, old, new):
        first_variable = variable_select.value
        plot.title.text = "Forecast accuracy of " + first_variable
        forecast_devs_df = combined_forecast_accuracy[variable_select.value]
        plot.yaxis.axis_label = variables_with_unit[variables_dict[first_variable]]
        for city_id in range(len(locations)):
            muted = lines[city_id].muted
            plot.renderers.remove(lines[city_id])
            lines[city_id] = plot.line([0, 1, 2, 3, 4, 5, 6, 7], forecast_devs_df.loc[:, locations[city_id]],
                                       color=Bokeh6[city_id + 1], width=3, legend_label=locations[city_id])
            lines[city_id].muted = muted
            hover = HoverTool(tooltips=[
                (locations[city_id], f"@y {units[first_variable]}, @x days before")
            ], renderers=[lines[city_id]])
            plot.add_tools(hover)

    variable_select = Select(title="Variable:", value=variables[0], options=variables)
    variable_select.on_change('value', update_plot)

    curdoc().add_root(column(variable_select, plot))
    curdoc().title = "forecast_accuracy_full_chart"


def create_chart_by_city(forecast_accuracy):

    plot = figure(width=1400, height=600, x_axis_type="datetime", toolbar_location=None)

    first_variable = variables[0]
    first_location = locations[0]
    forecast_devs_df = forecast_accuracy[0][0]
    title_text = "Forecast of " + first_variable + " in " + first_location
    plot.title.text = title_text

    lines = [0]*9
    datelist = pd.to_datetime(forecast_devs_df.loc[:, "datetime"], utc=True).to_list()
    items = []
    for forecast_from_day in range(7, -1, -1):
        col_name = first_variable + "_previous_day" + str(forecast_from_day)
        lines[forecast_from_day+1] = plot.line(datelist, forecast_devs_df.loc[:, col_name],
                                               color=Blues9[forecast_from_day], width=1, visible=False)
        items.append(("forecast from " + str(forecast_from_day) + " days before", [lines[forecast_from_day+1]]))
        hover = HoverTool(tooltips=[
            (f"forecast from {forecast_from_day} days before", f"@y {units[first_variable]}")
        ], renderers=[lines[forecast_from_day+1]])
        plot.add_tools(hover)
    lines[2].visible = True
    lines[4].visible = True
    lines[6].visible = True
    lines[0] = plot.line(pd.to_datetime(forecast_devs_df.loc[:, "datetime"], utc=True).to_list(),
                         forecast_devs_df.loc[:, first_variable], color=Bokeh6[0], width=1)
    items.append(("actual data", [lines[0]]))
    plot.x_range = Range1d(datelist[0], datelist[150])
    legend = Legend(items=items, location=(10, 300))
    plot.add_layout(legend, 'right')
    hover = HoverTool(tooltips=[
        (f"actual data", f"@y {units[first_variable]}")
    ], renderers=[lines[0]])
    plot.add_tools(hover)

    plot.xaxis.axis_label = "date"
    plot.yaxis.axis_label = variables_with_unit[0]

    plot.legend.click_policy = "hide"

    plot.xaxis.formatter = DatetimeTickFormatter(days="%d-%b")

    def update_plot(attr, old, new):
        first_variable = variable_select.value
        first_location = location_select.value
        plot.title.text = "Forecast of " + first_variable + " in " + first_location
        forecast_devs_df = forecast_accuracy[variables_dict[first_variable]][locations_dict[first_location]]
        plot.yaxis.axis_label = variables_with_unit[variables_dict[first_variable]]
        for forecast_from_day in range(7, -1, -1):
            visibility = lines[forecast_from_day+1].visible
            plot.renderers.remove(lines[forecast_from_day+1])
            col_name = first_variable + "_previous_day" + str(forecast_from_day)
            lines[forecast_from_day+1] = plot.line(datelist,
                                                 forecast_devs_df.loc[:, col_name],
                                                 color=Blues9[forecast_from_day], width=1, legend_label="forecast from " + str(forecast_from_day) + " days before")
            lines[forecast_from_day+1].visible = visibility
            hover = HoverTool(tooltips=[
                (f"forecast from {forecast_from_day} days before", f"@y {units[first_variable]}")
            ], renderers=[lines[forecast_from_day + 1]])
            plot.add_tools(hover)
        visibility = lines[0].visible
        plot.renderers.remove(lines[0])
        lines[0] = plot.line(datelist, forecast_devs_df.loc[:, first_variable], color=Bokeh6[0],
                             width=1, legend_label='actual data')
        lines[0].visible = visibility
        hover = HoverTool(tooltips=[
            (f"actual data", f"@y {units[first_variable]}")
        ], renderers=[lines[0]])
        plot.add_tools(hover)

    def update_axis(attr, old, new):
        plot.x_range.start = date_range_slider.value[0]
        plot.x_range.end = date_range_slider.value[1]

    date_range_slider = DateRangeSlider(value=(datelist[0], datelist[150]),
                                        start=datelist[0], end=datelist[-1])
    date_range_slider.on_change('value', update_axis)

    variable_select = Select(title="Variable:", value=variables[0], options=variables)
    variable_select.on_change('value', update_plot)

    location_select = Select(title="Location:", value=locations[0], options=locations)
    location_select.on_change('value', update_plot)

    layout = column(row(variable_select, location_select, date_range_slider), plot)
    curdoc().add_root(layout)
    curdoc().title = "forecast_accuracy_full_chart"


# def main():
#     pass
#
# if __name__ == "__main__":
#     main()
