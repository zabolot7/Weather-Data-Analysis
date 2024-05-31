import forecast_functions as f
from bokeh.plotting import figure, show
from bokeh.palettes import Bokeh6

def create_chart(avg_windspeeds):
    locations = ["Rovaniemi", "Warsaw", "Tripoli", "Kinshasa", "Cape_Town"]
    values = avg_windspeeds

    plot = figure(x_range=locations, title="Average wind speed by city", x_axis_label='city', y_axis_label='wind speed [km/h]')

    colors=[]
    for i in range(5):
        colors.append(Bokeh6[i+1])

    plot.vbar(x=locations, top=values, width=0.9, color=colors)

    plot.xgrid.grid_line_color = None
    plot.y_range.start = 0

    show(plot)

def main():
    avg_windspeeds = f.calculate_city_avg_windspeeds()
    create_chart(avg_windspeeds)

if __name__ == "__main__":
    main()