import pandas as pd

from bokeh.models import ColumnDataSource, Legend, HoverTool
from bokeh.palettes import Bokeh8
from bokeh.plotting import figure
from bokeh.io import show
from bokeh.transform import dodge

locations = ["New York", "Los Angeles", "Chicago", "Dallas", "Phoenix", "San Francisco", "Portland", "Nashville"]

Palette = Bokeh8

def download_us_cities():
    # dane pobrane ze strony https://simplemaps.com/data/us-cities

    us_cities_all = pd.read_csv("uscities.csv")
    us_cities_chosen = us_cities_all.loc[:, ["city", "population", "density"]]
    us_cities_chosen = us_cities_chosen[(us_cities_chosen.loc[:, "city"].isin(locations)) &
                                        (us_cities_chosen["population"] > 1000000)]
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
    city_avgs.reset_index(inplace=True, drop=True)
    city_avgs["city"] = pd.Series(locations)
    return city_avgs


def merge_population_aq():
    city_avgs = calculate_city_avgs()
    city_population = download_us_cities()
    full_df = city_population.merge(city_avgs, on="city")
    return full_df


def normalize_aq_population():
    aq_population_df = merge_population_aq()
    for column in aq_population_df.columns[1:]:
        aq_population_df[column] = aq_population_df[column] / aq_population_df[column].std()
    return aq_population_df


def create_plot():
    aq_values = merge_population_aq()
    aq_values.set_index("city", inplace=True, drop=True)
    aq_values.drop(["population", "density"], axis=1, inplace=True)
    aq_values.columns = ["pm10_1", "pm2_5_1", "carbon_monoxide_1",
                         "nitrogen_dioxide_1", "sulphur_dioxide_1"]
    aq_population_df = normalize_aq_population()
    aq_avg_norm = aq_population_df[["pm10", "pm2_5", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide"]].mean(axis=1)
    aq_population_df = aq_population_df.merge(aq_values, on="city", how="left")
    aq_population_df["aq_avg"] = aq_avg_norm.values

    source = ColumnDataSource(aq_population_df)
    plot = figure(x_range=locations, title="Air quality vs population", height=400, width=800, toolbar_location=None)
    variables = aq_population_df.columns[3:8]
    offset = -0.3
    items_aq = []
    for variable_id in range(len(variables)):
        vbar = plot.vbar(x=dodge("city", offset, range=plot.x_range), top=variables[variable_id],
                         source=source, width=0.12, color=Palette[variable_id+1])
        offset += 0.15
        items_aq.append((variables[variable_id], [vbar]))
        hover = HoverTool(tooltips=[
            (variables[variable_id], f"@{variables[variable_id]}_1" + " μg/m³")
        ], renderers=[vbar])
        plot.add_tools(hover)

    population_line = plot.line(locations, aq_population_df["population"], width=3, color="#333333")
    density_line = plot.line(locations, aq_population_df["density"], width=3, color="#8b489c")
    aq_avg_line = plot.line(locations, aq_population_df["aq_avg"], width=3, color=Palette[0])

    items_aq.append(("population", [population_line]))
    items_aq.append(("population density", [density_line]))
    items_aq.append(("average air quality", [aq_avg_line]))
    legend = Legend(items=items_aq, location=(10, 150))
    plot.add_layout(legend, "right")

    plot.legend.click_policy = "hide"
    plot.yaxis.visible = False

    show(plot)


def main():
    create_plot()


if __name__ == "__main__":
    main()
