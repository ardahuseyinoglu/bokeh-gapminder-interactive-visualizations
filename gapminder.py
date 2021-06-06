# LIBRARIES
import pandas as pd
import numpy as np
from bokeh.io import output_notebook, show, curdoc
from bokeh.plotting import figure
from bokeh.models import HoverTool, ColumnDataSource, CategoricalColorMapper
from bokeh.models import Slider, Select, RadioGroup, CheckboxGroup
from bokeh.palettes import Spectral6, Spectral10
from bokeh.layouts import row, widgetbox
from bokeh.transform import factor_cmap
from bokeh.models.tools import TapTool, CrosshairTool
from bokeh.models.widgets import Panel, Tabs
from bokeh.models import HoverTool
import copy 


# READ/CLEAN DATA
data = pd.read_csv("gapminder_tidy.csv")
data = data.set_index("Year")


# CREATE PLOTS AND WIDGETS
source = ColumnDataSource(data={
    'x'       : data.loc[1970].fertility,
    'y'       : data.loc[1970].life,
    'country' : data.loc[1970].Country,
    'pop'     : (data.loc[1970].population / 20000000) + 2,
    'region'  : data.loc[1970].region,
})


xmin, xmax = min(data.fertility), max(data.fertility)
ymin, ymax = min(data.life), max(data.life)

regions_list = data.region.unique().tolist()
color_mapper = CategoricalColorMapper(factors=regions_list, palette=Spectral6)
hover = HoverTool(tooltips=[('Country', '@country')])

plot = figure(title='Gapminder Data for 1970',
              x_axis_label='Fertility (children per woman)',
              y_axis_label='Life Expectancy (years)',
              plot_height=400, plot_width=700,
              x_range=(xmin, xmax), 
              y_range=(ymin, ymax))

plot.add_tools(hover)
plot.add_tools(TapTool())

plot.circle(x='x', y='y', 
            fill_alpha=0.7, 
            source=source,
            color=dict(field='region', transform=color_mapper), 
            legend='region',
            selection_color=dict(field='region', transform=color_mapper), 
            nonselection_fill_alpha=0.1,
            nonselection_fill_color="gray",
            nonselection_line_color="gray",
            nonselection_line_alpha=0.1)

plot.legend.location = 'bottom_left'


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


bool_result = pd.notnull(data.loc[1970, "fertility"]) & pd.notnull(data.loc[1970, "life"])
data_yr = data.loc[1970]
country_list=data_yr[bool_result].Country.unique().tolist()
country_list = ['--All--'] + country_list
country_select = Select(
    options=country_list,
    value='--All--',
    title='Country'
)


#second panel: population

all_countries = data.Country.unique().tolist()
years = range(1964, 2014)
all_source_pop = []
for country_name in all_countries:
    if (country_name == 'Tokelau') or (country_name == 'Åland'):
        continue
    source_pop = ColumnDataSource(data={
        'x'       : years,
        'y'       : (data[data.Country == country_name].population/ 1000000),
        'region'  : data[data.Country == country_name].region,
    })
    all_source_pop.append(source_pop)


xmin, xmax = min(data.index), max(data.index)
ymin, ymax = (min(data.population) / 1000000), (max(data.population) / 1000000)


plot_pop = figure(title='Population vs. Year',
              x_axis_label='Years',
              y_axis_label='Population',
              plot_height=400, plot_width=700,
              x_range=(xmin, xmax), 
              y_range=(ymin, ymax))


hover = HoverTool(tooltips=[('Year', '@x'), 
                            ('Population', '@y')], 
                  mode='vline')

plot_pop.add_tools(hover)
plot_pop.add_tools(CrosshairTool())


all_countries = data.Country.unique().tolist()
all_countries.remove('Tokelau') 
all_countries.remove('Åland') 
checkbox_pop = CheckboxGroup(labels=all_countries)



# ADD CALLBACKS
def update_plot(attr, old, new):
    yr = slider.value
    x = x_select.value
    y = y_select.value
    
    bool_result = pd.notnull(data.loc[yr, x]) & pd.notnull(data.loc[yr, y])
    data_yr = data.loc[yr]
    country_list = data_yr[bool_result].Country.unique().tolist()
    country_list = ['--All--'] + country_list
    country_select.options = country_list
    
    plot.xaxis.axis_label = x
    plot.yaxis.axis_label = y
    
    new_data = {
        'x'       : data.loc[yr][x],
        'y'       : data.loc[yr][y],
        'country' : data.loc[yr].Country,
        'pop'     : (data.loc[yr].population / 20000000) + 2,
        'region'  : data.loc[yr].region,
    }
    
    source.data = new_data
    
    plot.x_range.start = min(data[x])
    plot.x_range.end = max(data[x])
    plot.y_range.start = min(data[y])
    plot.y_range.end = max(data[y])
    
    plot.title.text = 'Gapminder data for %d' % yr
    
def update_plot_country_select(attr, old, new):
    yr = slider.value
    x = x_select.value
    y = y_select.value
    selected_country = country_select.value
    if selected_country == '--All--': 
        source.selected.indices = []
    else : 
        bool_result = pd.notnull(data.loc[yr, x]) & pd.notnull(data.loc[yr, y])
        data_yr = data.loc[yr]
        country_list=data_yr[bool_result].Country.unique().tolist()
        country_index = country_list.index(selected_country)
        source.selected.indices = [country_index]    
    
    plot.xaxis.axis_label = x
    plot.yaxis.axis_label = y
    
    new_data = {
        'x'       : data.loc[yr][x],
        'y'       : data.loc[yr][y],
        'country' : data.loc[yr].Country,
        'pop'     : (data.loc[yr].population / 20000000) + 2,
        'region'  : data.loc[yr].region,
    }
    
    source.data = new_data
    
    plot.x_range.start = min(data[x])
    plot.x_range.end = max(data[x])
    plot.y_range.start = min(data[y])
    plot.y_range.end = max(data[y])
    
    plot.title.text = 'Gapminder data for %d' % yr
    


    
    
all_countries = np.array(all_countries)
prev_active_countries_indices = [] 
    
def update_curdoc(active):
    active_countries_indices = active
    #active_countries = all_countries[active_countries_indices].tolist()
    rootLayout = curdoc().get_model_by_name('plot_pop')
    listOfSubLayouts = rootLayout.children

    #adding
    if len(active_countries_indices) > len(prev_active_countries_indices):
        added_country_index = (set(active_countries_indices) - set(prev_active_countries_indices)).pop()
        plot_pop.line(x='x', y='y', source=all_source_pop[added_country_index], name=str(added_country_index) + "_plot_pop" + "_line")
        plot_pop.circle(x='x', y='y', source=all_source_pop[added_country_index], fill_color='white', hover_color='red', size=4, name=str(added_country_index) + "_plot_pop" + "_circle")
        prev_active_countries_indices.append(added_country_index)
        
    #removing
    elif len(active_countries_indices) < len(prev_active_countries_indices):
        removed_country_index = (set(prev_active_countries_indices) - set(active_countries_indices)).pop()
        removed_plot_line = plot_pop.select(name=str(removed_country_index) + "_plot_pop" + "_line")
        removed_plot_circle = plot_pop.select(name=str(removed_country_index) + "_plot_pop" + "_circle")
        plot_pop.renderers.remove(removed_plot_line[0])
        plot_pop.renderers.remove(removed_plot_circle[0])
        prev_active_countries_indices.remove(removed_country_index)
        
    curr_selected_countries = all_countries[prev_active_countries_indices].tolist()
    min_pop = []
    max_pop = []
    for country in curr_selected_countries:
        min_pop.append(min(data[data.Country == country].population))
        max_pop.append(max(data[data.Country == country].population))
        
    plot_pop.y_range.start = min(min_pop) / 1000000
    plot_pop.y_range.end = max(max_pop) / 1000000
    

           
    
slider.on_change('value', update_plot)
x_select.on_change('value', update_plot)
y_select.on_change('value', update_plot)
country_select.on_change('value', update_plot_country_select)
checkbox_pop.on_click(update_curdoc) 

# ARRANGE PLOTS AND WIDGETS IN LAYOUTS
#layout = row(widgetbox(slider, x_select, y_select, country_select), plot)

first_panel = Panel(child=row(widgetbox(slider, x_select, y_select, country_select), plot), title='x-y scatters') # you can also use row insted column.
second_panel = Panel(child=row(widgetbox(checkbox_pop), plot_pop, name='plot_pop'), title='population')

tabs = Tabs(tabs=[first_panel, second_panel])


curdoc().add_root(tabs)
curdoc().title = 'Gapminder'