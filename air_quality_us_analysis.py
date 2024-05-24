import pandas as pd
import scipy

from scipy import stats

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import Range1d, Select, DateRangeSlider, DatetimeTickFormatter, ColumnDataSource, FactorRange
from bokeh.palettes import Bokeh8
from bokeh.plotting import figure
from bokeh.io import show

locations = ["New York", "Los Angeles", "Chicago", "Dallas", "Phoenix", "San Francisco", "Portland", "Nashville"]


def download_us_cities():
    # dane pobrane ze strony https://simplemaps.com/data/us-cities

    us_cities_all = pd.read_csv("uscities.csv")
    us_cities_chosen = us_cities_all.loc[:, ["city", "population", "density"]]
    us_cities_chosen = us_cities_chosen[(us_cities_chosen.loc[:, "city"].isin(locations)) & (us_cities_chosen["population"] > 1000000)]
    us_cities_chosen.reset_index(inplace=True, drop=True)
    return us_cities_chosen


def get_air_quality(city):
    filename = "air_quality_us_" + city + ".csv"
    city_aq_df = pd.read_csv(filename)
    city_aq_df = city_aq_df.loc[:, ~city_aq_df.columns.str.contains('^Unnamed')]
    city_aq_df.drop(["date"], axis=1, inplace=True)
    city_aq_avg_df = city_aq_df.mean().to_frame().T
    return city_aq_avg_df


def calculate_city_avgs():
    city_avgs = pd.DataFrame()
    for location in locations:
        current_avgs = get_air_quality(location)
        city_avgs = pd.concat([city_avgs, current_avgs], axis=0)
    # city_avgs.set_index(pd.Series(locations), inplace=True)
    city_avgs.reset_index(inplace=True, drop=True)
    city_avgs["city"] = pd.Series(locations)
    return city_avgs


def merge_population_aq():
    city_avgs = calculate_city_avgs()
    city_population = download_us_cities()
    full_df = city_population.merge(city_avgs, on="city")
    return full_df


# def standardise_aq_population():
#     aq_population_df = merge_population_aq()
#     for column in aq_population_df.columns[1:]:
#         aq_population_df[column] = stats.zscore(aq_population_df[column])
#     return aq_population_df


def normalize_aq_population():
    aq_population_df = merge_population_aq()
    for column in aq_population_df.columns[1:]:
        aq_population_df[column] = aq_population_df[column] / aq_population_df[column].std()
    return aq_population_df


def create_plot():
    # aq_population_df = merge_population_aq()
    aq_population_df = normalize_aq_population()

    labels = [(location, variable) for location in locations for variable in aq_population_df.columns[3:]]
    counts = sum(zip(aq_population_df["pm10"], aq_population_df["pm2_5"], aq_population_df["carbon_monoxide"],
                     aq_population_df["nitrogen_dioxide"], aq_population_df["sulphur_dioxide"]), ())

    source = ColumnDataSource(data=dict(x=labels, counts=counts))

    plot = figure(x_range=FactorRange(*labels), height=350, title="Air Quality",
               toolbar_location=None, tools="")

    plot.vbar(x='x', top='counts', width=0.9, source=source)
    plot.line(locations, aq_population_df["population"], width=3, color="red")
    plot.line(locations, aq_population_df["density"], width=3, color="green")

    plot.y_range.start = 0
    plot.x_range.range_padding = 0.1
    plot.xaxis.major_label_orientation = 1
    plot.xgrid.grid_line_color = None

    show(plot)


create_plot()

