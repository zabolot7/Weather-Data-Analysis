from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Select
from bokeh.plotting import figure
from bokeh.layouts import column

# Sample data for the first plot
x1 = list(range(10))
y1 = [i**2 for i in x1]
source1 = ColumnDataSource(data=dict(x=x1, y=y1))

# Sample data for the second plot
x2 = list(range(10))
y2 = [i*2 for i in x2]
source2 = ColumnDataSource(data=dict(x=x2, y=y2))

# Create a plot
plot = figure(title="Interactive Plot with Dropdown", x_axis_label='X-axis', y_axis_label='Y-axis')

# Create a line glyph and add it to the plot
line = plot.line('x', 'y', source=source1, line_width=2, color='blue')

# Create a data source that will be updated by the dropdown
source = ColumnDataSource(data=dict(x=x1, y=y1))

# Callback function to update the plot
def update_plot(attr, old, new):
    if dropdown.value == 'Dataset 1':
        source.data = dict(source1.data)
        plot.title.text = "Dataset 1: y = x^2"
    else:
        source.data = dict(source2.data)
        plot.title.text = "Dataset 2: y = 2x"

# Update the line glyph to use the new source
line.data_source = source

# Dropdown menu
dropdown = Select(title="Select Dataset", value="Dataset 1", options=["Dataset 1", "Dataset 2"])
dropdown.on_change("value", update_plot)

# Layout
layout = column(dropdown, plot)

# Add the layout to the current document
curdoc().add_root(layout)