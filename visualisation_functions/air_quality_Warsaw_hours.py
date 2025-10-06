import pandas as pd

from bokeh.models import Range1d
from bokeh.plotting import figure
from bokeh.io import show


def get_air_quality():
    filename = "air_quality_Warsaw.csv"
    warsaw_aq_df = pd.read_csv(filename)
    warsaw_aq_df = warsaw_aq_df.loc[:, ~warsaw_aq_df.columns.str.contains('^Unnamed')]
    warsaw_aq_df["hour"] = pd.to_datetime(warsaw_aq_df.loc[:, "date"], utc=True).dt.hour
    warsaw_aq_df.drop(["date"], axis=1, inplace=True)
    warsaw_aq_df = warsaw_aq_df.groupby("hour").mean()
    return warsaw_aq_df


def create_plot():
    tooltips = [("hour", "$index"), ("pm 2.5", "$y")]
    plot = figure(width=800, height=400, tooltips=tooltips)
    plot.title = "Average pm 2.5 in Warsaw by time of the day"

    warsaw_aq_df = get_air_quality()
    hours = list(range(0, 24))
    plot.x_range = Range1d(0, 23)
    plot.line(hours, warsaw_aq_df.loc[:, "pm2_5"], color="red", width=3)

    plot.xaxis.axis_label = "hour"
    plot.yaxis.axis_label = "pm 2.5"

    show(plot)


def main():
    create_plot()


if __name__ == "__main__":
    main()
