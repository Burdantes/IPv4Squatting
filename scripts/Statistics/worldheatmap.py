import csv
import plotly
import plotly.offline as py
import plotly.graph_objs as go
import pandas as pd
import pycountry

input_countries = ['American Samoa', 'Canada', 'France']

import pycountry_convert as pc

def country_to_continent(country_alpha2):
    country_continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
    country_continent_name = pc.convert_continent_code_to_continent_name(country_continent_code)
    return country_continent_name

# Example
# country_name = 'Germany'
# print(country_to_continent(country_name))

countries = {}
from collections import defaultdict
continents = defaultdict(lambda: 0)
for country in pycountry.countries:
    countries[country.alpha_2] = country.alpha_3
#color ramp for chloropleth map
scl = [[0.0, 'rgb(242,240,247)'],[0.2, 'rgb(218,218,235)'],[0.4, 'rgb(188,189,220)'], [0.6, 'rgb(158,154,200)'],[0.8, 'rgb(117,107,177)'],[1.0, 'rgb(84,39,143)']]
top_countries = pd.read_csv('../../result/squatters_metainfo.csv',index_col = 0)
print(top_countries)
top_countrie = top_countries['Country'].value_counts()
print(top_countries)
top_countries = pd.DataFrame()
top_countries['value'] = top_countrie
index = []
for n in top_countries.index:
    print(n)
    if n =='EU':
        index.append('RUS')
        continue
    continents[country_to_continent(n)] +=top_countries[top_countries.index == n].value[0]
    index.append(countries[n])
print(continents)
top_countries.index = index
print(top_countries['value'])
fig = go.Figure(
data = [ dict(
        type='choropleth',
        colorscale = 'blues',
        locations = top_countries.index,
        z = top_countries['value'],
        locationmode = ('ISO-3'),
        text = ('country: '+str(top_countries.index) + '<br>' +\
               'number of attacks: '+str(top_countries['value'])),
        marker = dict(
            line = dict (
                color = 'rgb(255,255,255)',
                width = 0.5
            )
        ),
        colorbar = dict(
            title = dict(text= "# of squatting organizations",
                    side = "right")
        )
    ) ],

layout = dict(
        # title = 'Geographic Distribution of the ASes that we have identified as fishy candidates',
        geo = dict(
            scope='world',
            projection=dict( type='natural earth' ),
            showlakes = True,
            landcolor = 'lightgray',
            showland = True,
            showcountries = True,
            countrycolor = 'gray',
            countrywidth = 0.5,
            lakecolor = 'rgb(255, 255, 255)',
        ),
    )
)
fig.update_layout(
    font=dict(
        family="Arial",
        size=50,
        # color="RebeccaPurple"
    )
)
fig.write_image("../../result/fig_map+heatmap.png",width=1980, height=1080)
