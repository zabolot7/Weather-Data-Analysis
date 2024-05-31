import pandas as pd
import copy

from bokeh.palettes import Set1_3, Bokeh8
from bokeh.models import FactorRange, Range1d, ColumnDataSource, Legend, HoverTool
from bokeh.transform import factor_cmap, dodge
from bokeh.plotting import figure
from bokeh.io import show

def csv_into_df(cities_list):
    city_pollution_dfs_dict = {}
    for city in cities_list:
        filename = "pollution_" + city + ".csv"
        city_pollution_df = pd.read_csv(filename)
        city_pollution_df.drop("carbon_monoxide", axis=1, inplace=True)
        city_pollution_dfs_dict[city] = city_pollution_df
    return city_pollution_dfs_dict


def calculate_continent_avg_pollutions(city_pollution_dfs_dict, cities):
    city_avgs = pd.DataFrame()
    for city in cities:
        mean_pollution = copy.deepcopy(city_pollution_dfs_dict[city])
        mean_pollution = mean_pollution.drop("date", axis=1)
        mean_pollution = mean_pollution.mean().to_frame().transpose()
        mean_pollution.drop(mean_pollution.columns[0], axis=1, inplace=True)

        city_avgs = pd.concat([city_avgs, mean_pollution], axis=0)

    continent_avgs = city_avgs.mean().to_frame().transpose()

    return continent_avgs


def calculate_continent_median_pollutions(city_pollution_dfs_dict, cities):
    city_avgs = pd.DataFrame()
    for city in cities:
        mean_pollution = copy.deepcopy(city_pollution_dfs_dict[city])
        mean_pollution = mean_pollution.drop("date", axis=1)
        mean_pollution = mean_pollution.mean().to_frame().transpose()
        mean_pollution.drop(mean_pollution.columns[0], axis=1, inplace=True)

        city_avgs = pd.concat([city_avgs, mean_pollution], axis=0)

    continent_avgs = city_avgs.median().to_frame().transpose()

    return continent_avgs


def create_bar_chart(us_avgs, eu_avgs, variables, continents, type):
    bar_names = [(variable, continent) for variable in variables for continent in continents]

    results_us = us_avgs.loc[0].tolist()
    results_eu = eu_avgs.loc[0].tolist()
    chart_data = sum(zip(results_us, results_eu), ())

    source = ColumnDataSource(data=dict(x=bar_names, counts=chart_data))

    TOOLTIPS = [
        ("value", "@counts" + " μg/m³")
    ]

    plot = figure(x_range=FactorRange(*bar_names), height=350, tooltips=TOOLTIPS, title= type + " pollution by location",
               toolbar_location=None, tools="")

    plot.vbar(x='x', top='counts', width=0.9, source=source, line_color="white", fill_color=factor_cmap('x', palette=Set1_3, factors=continents, start=1, end=2))

    plot.y_range = Range1d(0, 30)
    plot.xgrid.grid_line_color = None

    show(plot)


def calculate_city_avg_pollutions(city_pollution_dfs_dict, cities):
    city_avgs = pd.DataFrame()
    for city in cities:
        mean_pollution = copy.deepcopy(city_pollution_dfs_dict[city])
        mean_pollution = mean_pollution.drop("date", axis=1)
        mean_pollution = mean_pollution.mean().to_frame().transpose()
        mean_pollution.drop(mean_pollution.columns[0], axis=1, inplace=True)

        city_avgs = pd.concat([city_avgs, mean_pollution], axis=0)
    city_avgs = city_avgs.T
    city_avgs.columns = cities

    return city_avgs


def create_full_chart_compare_cities(us_city_avgs, cities_us, eu_city_avgs, cities_eu):
    us_city_avgs = copy.deepcopy(us_city_avgs).T
    eu_city_avgs = copy.deepcopy(eu_city_avgs).T
    city_avgs = pd.concat([us_city_avgs, eu_city_avgs])
    locations = cities_us + cities_eu

    print(city_avgs)
    print(locations)

    city_avgs.reset_index(inplace=True)
    source = ColumnDataSource(city_avgs)
    plot = figure(x_range=locations, title="Air quality by city", height=400, width=1000, toolbar_location=None)
    variables = city_avgs.columns
    offset = -0.3
    items = []
    for variable_id in range(len(variables)):
        vbar = plot.vbar(x=dodge("index", offset, range=plot.x_range), top=variables[variable_id], source=source,
                         width=0.12, color=Bokeh8[variable_id + 1])
        offset += 0.15
        items.append((variables[variable_id], [vbar]))
        hover = HoverTool(tooltips=[
            (variables[variable_id], f"@{variables[variable_id]}" + " μg/m³")
        ], renderers=[vbar])
        plot.add_tools(hover)

    legend = Legend(items=items[1:], location=(10, 150))
    plot.add_layout(legend, "right")

    plot.legend.click_policy = "hide"

    show(plot)


def main():
    variables = ["pm10", "pm2_5", "nitrogen_dioxide", "sulphur_dioxide"]
    cities_us = ["Phoenix", "Philadelphia", "San_Antonio", "San_Diego", "Dallas"]
    cities_eu = ["Budapest", "Barcelona", "Munich", "Prague", "Milan"]
    continents = ["us", "eu"]

    us_pollution_dfs_dict = csv_into_df(cities_us)
    eu_pollution_dfs_dict = csv_into_df(cities_eu)

    us_avgs = calculate_continent_avg_pollutions(us_pollution_dfs_dict, cities_us)
    eu_avgs = calculate_continent_avg_pollutions(eu_pollution_dfs_dict, cities_eu)

    us_medians = calculate_continent_median_pollutions(us_pollution_dfs_dict, cities_us)
    eu_medians = calculate_continent_median_pollutions(eu_pollution_dfs_dict, cities_eu)

    create_bar_chart(us_avgs, eu_avgs, variables, continents, type="average")

    create_bar_chart(us_medians, eu_medians, variables, continents, type="median")

    us_city_avgs = calculate_city_avg_pollutions(us_pollution_dfs_dict, cities_us)
    eu_city_avgs = calculate_city_avg_pollutions(eu_pollution_dfs_dict, cities_eu)

    create_full_chart_compare_cities(us_city_avgs, cities_us, eu_city_avgs, cities_eu)

if __name__ == "__main__":
    main()
