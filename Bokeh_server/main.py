
import pandas as pd
import numpy as np
from bokeh.io import *
from bokeh.layouts import *
from bokeh.models.widgets import *
from bokeh.models import *
from bokeh.plotting import *
from os.path import dirname, join

countries = ['Switzerland','United States', 'India','France', 'Italy','Australia','Singapore', 'Japan','Kenya','Brazil']
full_df = pd.read_csv('data_countries/0_Data_All_Countries.csv', index_col = ['Country', 'Year'])

x_labels = ['Household final consumption expenditure per capita (% change)','Merchandise imports from high-income economies (% of total merchandise imports)']
y_labels = list(y for y in full_df.columns if('%' in y and y not in x_labels))

current = full_df.loc[countries[0]]

year_slider = Slider(start=current.index[0], end=current.index[-1], value=current.index[0], step=1, title="Year")

select_x = Select(height=100, width = 110, title="Index on X axis :", value='Household final consumption expenditure per capita (% change)', options=x_labels)
select_y = Select(height=100, width = 110, title="Index on Y axis :", value='Inflation, consumer prices (annual %)', options=y_labels)

select_country = RadioGroup(labels= countries, active=0)

animation = Button(label='► Play', width=60)

def find_bar(y):
    first_elem = y.split('(')[0]
    if 'change' in y:
        second_elem = [elem for elem in full_df.columns if (first_elem in elem and '%' not in elem)]
        return second_elem[0]
    else:
        return y


source = ColumnDataSource(data = dict(
        x = full_df.loc[countries[select_country.active]].reset_index()[select_x.value].values,
        y = full_df.loc[countries[select_country.active]].reset_index()[select_y.value].values, 
        year = full_df.loc[countries[select_country.active]].reset_index()['Year'].values,
        x_bar = full_df.loc[countries[select_country.active]].reset_index()[find_bar(select_x.value)].values,
        y_bar = full_df.loc[countries[select_country.active]].reset_index()[find_bar(select_y.value)].values,
        x_radius = list(np.divide(full_df.loc[countries[select_country.active]].reset_index()[find_bar(select_x.value)].values, 3*max(full_df.loc[countries[select_country.active]].reset_index()[find_bar(select_x.value)].values))),
        y_radius = list(np.divide(full_df.loc[countries[select_country.active]].reset_index()[find_bar(select_y.value)].values, 6*max(full_df.loc[countries[select_country.active]].reset_index()[find_bar(select_y.value)].values)))))

hover = HoverTool(tooltips=[('Abs_val_X', '@x_bar'),('Abs_val_Y', '@y_bar'),("Year","@year")])

p = figure(plot_height=600, plot_width=700, title= countries[select_country.active],x_axis_label= select_x.value ,y_axis_label= select_y.value , tools=[ResetTool(), WheelZoomTool(),PanTool(), hover])
p.circle(x='x', y='y', source=source, radius = 'x_radius', fill_color ='aquamarine', fill_alpha=0.4, line_color='aquamarine')
p.circle(x='x', y='y', source=source, radius = 'y_radius', fill_color = 'coral', fill_alpha=0.95, line_color='aquamarine')
p.title.text_font_size = "20px"
p.title.align = 'center'
p.title.text_font = 'helvetica'
p.title.text_color = 'black'
p.grid.bounds = (0,0.00001)
p.grid.grid_line_color= 'grey'

def update(attr, old, new):
    p.xaxis.axis_label = select_x.value
    p.yaxis.axis_label = select_y.value
    this_year = year_slider.value
    selected_country = select_country.active
    p.title.text = countries[selected_country]
   
    full_x_bar = list(full_df.loc[countries[selected_country]][find_bar(select_x.value)].values)
    full_y_bar = list(full_df.loc[countries[selected_country]][find_bar(select_y.value)].values)
    


    source.data = dict(
        x = list(full_df.loc[countries[selected_country]][select_x.value].loc[:this_year+1].values),
        y = list(full_df.loc[countries[selected_country]][select_y.value].loc[:this_year+1].values),
        
        x_bar = list(full_df.loc[countries[selected_country]][find_bar(select_x.value)].loc[:this_year+1].values),
        y_bar = list(full_df.loc[countries[selected_country]][find_bar(select_y.value)].loc[:this_year+1].values),
         
        x_radius = list(np.divide(full_x_bar, 3*max(full_x_bar)))[:this_year+1-1990],
        y_radius = list(np.divide(full_y_bar, 6*max(full_y_bar)))[:this_year+1-1990],
              
        year =  list(full_df.loc[countries[selected_country]].reset_index()['Year'].values)[:this_year-1990+1]
        )
    
    
def update_animation_state():
    year = year_slider.value + 1
    if (year > full_df.index.levels[1][-1]):
        launch_stop_animation()
    else:
        year_slider.value = year  
    
def launch_stop_animation():
    if animation.label == '► Play':
        animation.label = '❚❚ Pause'
        curdoc().add_periodic_callback(update_animation_state, 1000)
    else:
        animation.label = '► Play'
        curdoc().remove_periodic_callback(update_animation_state)
      

big_title = Div(text=open(join(dirname(__file__), "description.html")).read(), width=1050)

   

controls_1 = [select_x,select_y,select_country]

select_x.on_change('value', update)
select_y.on_change('value', update)
year_slider.on_change('value', update)
select_country.on_change('active',update)
animation.on_click(launch_stop_animation)

inputs_1 = widgetbox(*controls_1, sizing_mode='scale_width')

layout = layout([[big_title],[inputs_1,p],[Spacer(height=50),year_slider,animation]],sizing_mode='fixed')

curdoc().add_root(layout)
curdoc().title = "Main"
