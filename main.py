import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from flask import Flask
import plotly.graph_objs as go
import numpy as np
import pandas as pd
import textwrap

server = Flask(__name__)
app = dash.Dash(__name__, server=server)
app.scripts.config.serve_locally = True
app.css.append_css({"external_url": "https://codepen.io/Maxwell8888/pen/YOWOam.css"})

# prepare data
agg = pd.read_csv('gva_aggregate_data_2016.csv')

# sub-sector level tables ======================================================
all_row_order = """Civil Society (Non-market charities)
Creative Industries
Cultural Sector
Digital Sector
Gambling
Sport
Telecoms
Tourism
All DCMS sectors
UK""".split('\n')
creative_row_order = """Advertising and marketing
Architecture 
Crafts 
Design and designer fashion 
Film, TV, video, radio and photography
IT, software and computer services
Publishing
Museums, galleries and Libraries 
Music, performing and visual arts""".split('\n')
digital_row_order = """Manufacturing of electronics and computers    
Wholesale of computers and electronics    
Publishing (excluding translation and interpretation activities)       
Software publishing       
Film, TV, video, radio and music   
Telecommunications        
Computer programming, consultancy and related activities        
Information service activities      
Repair of computers and communication equipment""".split('\n')
culture_row_order = """Arts
Film, TV and music
Radio
Photography
Crafts
Museums and galleries
Library and archives
Cultural education
Heritage""".split('\n')
row_orders = {
    'Creative Industries': creative_row_order,
    'Digital Sector': digital_row_order,
    'Cultural Sector': culture_row_order,
    'All': all_row_order
}


def make_table(sector, indexed=False):
    df = agg.copy()
    if sector == 'All':
        df = agg.loc[agg['sub-sector'] == 'All']
        breakdown_col = 'sector'
        df['gva'] = df['gva'] / 1000 # covnert sector level to be in bn's
    else:
        df = agg.loc[agg['sector'] == sector]
        breakdown_col = 'sub-sector'        

    tb = pd.crosstab(df[breakdown_col], df['year'], values=df['gva'], aggfunc=sum)
    
    tb = tb.reindex(row_orders[sector])
    
    if indexed:
        data = tb.copy()
        tb.loc[:, 2010] = 100
        for y in range(2011, max(agg.year) + 1):
            tb.loc[:, y] = data.loc[:, y] / data.loc[:, 2010] * 100

    tb = round(tb, 5)
    return tb

app.layout = html.Div([

html.Header([
        html.Div([
            html.A([
                html.Img(src='https://github.com/DCMSstats/images/raw/master/logo-gov-white.png', id='gov-logo'),
                html.Div(['DCMS Statistics'], id='header-stat-text'),
                ], 
                href='https://www.gov.uk/government/organisations/department-for-digital-culture-media-sport/about/statistics',
                id='header-stat-link'),
            html.Div(['BETA'], id='beta'),
            html.Div([
                html.P(['Give us '], id='feedback-text'), 
                html.A(
                    ['feedback'], 
                    href='mailto:evidence@culture.gov.uk?subject=Museum visits dashboard feedback',
                    id='feedback-link'
                )
            ], 
            id='feedback'),
        ],
        id='header-content',
        ),
],
),

html.Div([
html.H1('DCMS Economic Estimates - GVA', className='myh1'),

html.Div([dcc.Markdown('''
Updated to include 2016 data.

This tool shows GVA for DCMS sectors. It is based on [National Accounts](https://www.ons.gov.uk/economy/nationalaccounts) and [Annual Business Survey](https://www.ons.gov.uk/ons/rel/abs/annual-business-survey/index.html) data.

To help ensure the information in this dashboard is transparent, the data used is pulled directly from [gov.uk/government/organisations/department-for-digital-culture-media-sport/about/statistics](https://www.gov.uk/government/organisations/department-for-digital-culture-media-sport/about/statistics) which has information about the data and a [preview](https://www.gov.uk/government/organisations/department-for-digital-culture-media-sport/about/statistics), and the dashboard's [source code](https://github.com/DCMSstats/gva_webapp) is [open source](https://www.gov.uk/service-manual/technology/making-source-code-open-and-reusable) with an [Open Government Licence](http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
            ''')], id='preamble', className='markdown mysection'),

html.Section([
        
html.Div([
dcc.Dropdown(
    id='breakdown-dropdown',
    className='mydropdown',
    options=[{'label': k, 'value': v} for k,v in {'DCMS Sectors': 'All', 'Creative Industries sub-sectors': 'Creative Industries', 'Digital sub-sectors': 'Digital Sector', 'Cultural sub-sectors': 'Cultural Sector'}.items()],
    value='Creative Industries'
),
dcc.Dropdown(
    id='indexed-dropdown',
    className='mydropdown',
    options=[{'label': i, 'value': i} for i in ['Value', 'Indexed']],
    value='Value'
),
#dcc.Dropdown(
#    id='cvm-dropdown',
#    className='mydropdown',
#    options=[{'label': i, 'value': i} for i in ['Current Price (not adjusted for inflation)',
##             'Chained Volume Measure (adjusted for inflation)'
#             ]],
#    value='Current Price (not adjusted for inflation)'
#),
], id='dropdowns'),
        
dcc.Graph(id='ts-graph', config={'displayModeBar': False}),
], className='mysection'),
], id='main'),

html.Div([
dcc.Markdown('''
Contact Details: For any queries please telephone 020 7211 6000 or email evidence@culture.gov.uk

![Image](https://github.com/DCMSstats/images/raw/master/open-gov-licence.png) All content is available under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/) except where otherwise stated
''', className='markdown')
#    html.Img(src='https://github.com/DCMSstats/images/raw/master/open-gov-licence.png', className='ogl-logo'),

], id='myfooter')

], id='wrapper')

trace_name = 'The quick brows fox jumps over the lazy log'
legend_str = '<br>'.join(textwrap.wrap(trace_name, width=26))
@app.callback(Output('ts-graph', 'figure'), [Input('breakdown-dropdown', 'value'), Input('indexed-dropdown', 'value')])
def update_graph(breakdown, indexed):
    
    
    indexed_bool = False
    if indexed == 'Indexed':
        indexed_bool = True
        yaxis_title = ''
    else:
        if breakdown == 'All':
            yaxis_title = '£bn'
        else:
            yaxis_title = '£m'
    tb = make_table(breakdown, indexed_bool)
    traces = []
    for i in tb.index:
        traces.append(go.Scatter(
            x=list(tb.columns),
            y=list(tb.loc[i, :].values),
            mode = 'lines+markers',
            name=i
#            name='<br>'.join(textwrap.wrap(i, width=30))
        ))    
    
    layout = dict(
        title='Current Price (not adjusted for inflation)',
        height = 600,
        margin = dict(l=80, r=0, t=80, b=100, pad=0),
        yaxis = dict(title = yaxis_title, tickformat = ','),
        legend = dict(x=.01, y=-0.8),
        xaxis = dict(tickmode='array', 
                     tickvals = [2010, 2011, 2012, 2013, 2014, 2015, 2016],
                     ticktext = [2010, 2011, 2012, 2013, 2014, 2015, '2016 (p)'])
    )
    return dict(data=traces, layout=layout)
    

if __name__ == '__main__':
    app.run_server()
