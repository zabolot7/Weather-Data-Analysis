import numpy as np
import pandas as pd

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import Range1d, Select, DateRangeSlider, DatetimeTickFormatter, Legend, HoverTool
from bokeh.palettes import Bokeh6, Blues9, Set1_3
from bokeh.plotting import figure
from bokeh.io import show
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.plotting import figure, show
from bokeh.transform import factor_cmap


def csv_into_df(cities_list):
    city_pollution_dfs_dict = {}
    for city in cities_list:
        filename = "pollution_" + city + ".csv"
        city_pollution_df = pd.read_csv(filename)
        city_pollution_dfs_dict[city] = city_pollution_df
    return city_pollution_dfs_dict


def calculate_global_stdevs(us_city_pollution_dfs_dict, eu_city_pollution_dfs_dict):
    global_city_pollution_dfs_dict = us_city_pollution_dfs_dict | eu_city_pollution_dfs_dict # merges two dicts

    global_pollution_data_df = pd.DataFrame()
    for city in global_city_pollution_dfs_dict:
        city_pollution_df = global_city_pollution_dfs_dict[city]
        city_pollution_df.drop("date", axis=1, inplace=True)
        global_pollution_data_df = pd.concat([global_pollution_data_df, city_pollution_df], axis=0)

    global_stdevs_dict = {}
    for column in city_pollution_df.columns[1:]:
        global_stdevs_dict[column] = city_pollution_df[column].std()

        # global_stdevs.append(city_pollution_df[column].std())

    return global_stdevs_dict


def calculate_continent_avg_pollutions(city_pollution_dfs_dict, cities):
    city_avgs = pd.DataFrame()
    for city in cities:
        mean_pollution = city_pollution_dfs_dict[city].drop("date", axis=1)
        mean_pollution = mean_pollution.mean().to_frame().transpose()
        mean_pollution.drop(mean_pollution.columns[0], axis=1, inplace=True)

        city_avgs = pd.concat([city_avgs, mean_pollution], axis=0)

    continent_avgs = city_avgs.mean().to_frame().transpose()

    return continent_avgs


def calculate_normalised_continent_avg_pollutions(city_pollution_dfs_dict, cities, global_stdevs_dict):
    city_avgs = pd.DataFrame()
    for city in cities:
        # mean_pollution = city_pollution_dfs_dict[city].drop("date", axis=1)
        mean_pollution = city_pollution_dfs_dict[city]

        for variable in mean_pollution.columns[1:]: # normalising
            normalise_by = global_stdevs_dict[variable]
            mean_pollution[variable] = (mean_pollution[variable] / normalise_by).round(3)

        mean_pollution = mean_pollution.mean().to_frame().transpose()
        mean_pollution.drop(mean_pollution.columns[0], axis=1, inplace=True)

        city_avgs = pd.concat([city_avgs, mean_pollution], axis=0)

    continent_avgs = city_avgs.mean().to_frame().transpose()

    return continent_avgs


def create_bar_chart(us_avgs, eu_avgs, variables, continents):
    bar_names = [(variable, continent) for variable in variables for continent in continents]

    results_us = us_avgs.loc[0].tolist()
    results_eu = eu_avgs.loc[0].tolist()
    chart_data = sum(zip(results_us, results_eu), ())

    source = ColumnDataSource(data=dict(x=bar_names, counts=chart_data))

    TOOLTIPS = [
        ("value", "@counts" + " μg/m³")
    ]

    plot = figure(x_range=FactorRange(*bar_names), height=350, tooltips=TOOLTIPS, title="average pollution by location",
               toolbar_location=None, tools="")

    plot.vbar(x='x', top='counts', width=0.9, source=source, line_color="white", fill_color=factor_cmap('x', palette=Set1_3, factors=continents, start=1, end=2))

    plot.y_range.start = 0
    plot.xgrid.grid_line_color = None

    show(plot)

def create_normalised_bar_chart(us_avgs, eu_avgs, variables, continents, label_data):
    bar_names = [(variable, continent) for variable in variables for continent in continents]

    results_us = us_avgs.loc[0].tolist()
    results_eu = eu_avgs.loc[0].tolist()
    chart_data = sum(zip(results_us, results_eu), ())

    labels = []
    for i in range(len(variables)):
        labels.append(label_data[0][i])
        labels.append(label_data[1][i])

    source = ColumnDataSource(data=dict(x=bar_names, counts=chart_data, desc=labels))

    TOOLTIPS = [
        ("value", "@desc" + " μg/m³"),
    ]

    plot = figure(x_range=FactorRange(*bar_names), height=350, tooltips=TOOLTIPS, title="normalised average pollution by location",
                  toolbar_location=None, tools="")

    plot.vbar(x='x', top='counts', width=0.9, source=source, line_color="white",
              fill_color=factor_cmap('x', palette=Set1_3, factors=continents, start=1, end=2))

    plot.y_range.start = 0
    plot.x_range.range_padding = 0.1
    plot.xgrid.grid_line_color = None
    plot.yaxis.visible = False

    show(plot)


def main():
    variables = ["pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide"]
    cities_us = ["Phoenix", "Philadelphia", "San_Antonio", "San_Diego", "Dallas"]
    cities_eu = ["Budapest", "Barcelona", "Munich", "Prague", "Milan"]
    continents = ["us", "eu"]

    us_pollution_dfs_dict = csv_into_df(cities_us)
    eu_pollution_dfs_dict = csv_into_df(cities_eu)

    us_avgs = calculate_continent_avg_pollutions(us_pollution_dfs_dict, cities_us)
    eu_avgs = calculate_continent_avg_pollutions(eu_pollution_dfs_dict, cities_eu)

    global_stdevs_dict = calculate_global_stdevs(us_pollution_dfs_dict, eu_pollution_dfs_dict)

    normalised_us_avgs = calculate_normalised_continent_avg_pollutions(us_pollution_dfs_dict, cities_us, global_stdevs_dict)
    normalised_eu_avgs = calculate_normalised_continent_avg_pollutions(eu_pollution_dfs_dict, cities_eu, global_stdevs_dict)

    # create_bar_chart(us_avgs, eu_avgs, variables, continents)
    create_normalised_bar_chart(normalised_us_avgs, normalised_eu_avgs, variables, continents, [us_avgs.values[0], eu_avgs.values[0]])


if __name__ == "__main__":
    main()
