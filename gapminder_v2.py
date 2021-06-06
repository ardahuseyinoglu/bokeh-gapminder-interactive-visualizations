# LIBRARIES
import pandas as pd
from bokeh.io import output_notebook, show, curdoc
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource, CategoricalColorMapper
from bokeh.models import Slider, Select, RadioGroup
from bokeh.palettes import Spectral6
from bokeh.layouts import row, widgetbox
from bokeh.transform import factor_cmap
from bokeh.models.tools import TapTool

# READ/CLEAN DATA
data = pd.read_csv("gapminder_tidy.csv")
data = data.set_index("Year")
regions_list = data.region.unique().tolist()


# CREATE PLOTS AND WIDGETS
all_sources = []
for region in regions_list:
    source = ColumnDataSource(data={
    'x'       : data[(data.index == 1970) & (data.region == region)].fertility,
    'y'       : data[(data.index == 1970) & (data.region == region)].life,
    'country' : data[(data.index == 1970) & (data.region == region)].Country,
    'pop'     : (data[(data.index == 1970) & (data.region == region)].population / 20000000) + 2
    })
    all_sources.append(source)


xmin, xmax = min(data.fertility), max(data.fertility)
ymin, ymax = min(data.life), max(data.life)


plot = figure(title='Gapminder Data for 1970',
              x_axis_label='Fertility (children per woman)',
              y_axis_label='Life Expectancy (years)',
              plot_height=400, plot_width=700,
              x_range=(xmin, xmax), 
              y_range=(ymin, ymax))

hover = HoverTool(tooltips=[('Country', '@country')])
plot.add_tools(hover)
plot.add_tools(TapTool())

for source, name, color in zip(all_sources, regions_list, Spectral6):
    plot.circle(x='x', y='y', 
                fill_alpha=0.7, 
                source=source,
                color=color,
                selection_color="firebrick", 
                nonselection_fill_alpha=0.05,
                nonselection_fill_color=color,
                nonselection_line_color=color,
                nonselection_line_alpha=0.05, 
                muted_color=color, 
                muted_alpha=0.05,
                legend_label=name)

    
plot.legend.location = 'top_right'
plot.legend.click_policy= 'mute'


# Slider for year
slider = Slider(start=1970, end=2010, step=1, value=1970, title='Year')

# Create a dropdown Select widget for the x data: x_select
x_select = Select(
    options=['fertility', 'life', 'child_mortality', 'gdp'],
    value='fertility',
    title='x-axis data'
)

# Create a dropdown Select widget for the y data: y_select
y_select = Select(
    options=['fertility', 'life', 'child_mortality', 'gdp'],
    value='life',
    title='y-axis data'
)

options_country = data.Country.unique().tolist()
options_country = ['--All--'] + options_country
country_select = Select(
    options=options_country,
    value='all',
    title='Country'
)

# ADD CALLBACKS
def update_plot(attr, old, new):
    yr = slider.value
    x = x_select.value
    y = y_select.value
    #selected_country = country_select.value
    #print(source.selected)
    
    plot.xaxis.axis_label = x
    plot.yaxis.axis_label = y
    
    for region, source in zip(regions_list, all_sources):
        new_data = {
        'x'       : data[(data.index == yr) & (data.region == region)][x],
        'y'       : data[(data.index == yr) & (data.region == region)][y],
        'country' : data[(data.index == yr) & (data.region == region)].Country,
        'pop'     : (data[(data.index == yr) & (data.region == region)].population / 20000000) + 2
        }
        source.data = new_data
    
    
    
    plot.x_range.start = min(data[x])
    plot.x_range.end = max(data[x])
    plot.y_range.start = min(data[y])
    plot.y_range.end = max(data[y])
    
    plot.title.text = 'Gapminder data for %d' % yr
    
    
slider.on_change('value', update_plot)
x_select.on_change('value', update_plot)
y_select.on_change('value', update_plot)
country_select.on_change('value', update_plot)


# ARRANGE PLOTS AND WIDGETS IN LAYOUTS
layout = row(widgetbox(slider, x_select, y_select, country_select), plot)


curdoc().add_root(layout)
curdoc().title = 'Gapminder'