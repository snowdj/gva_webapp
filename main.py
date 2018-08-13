import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from flask import Flask
import numpy as np
import pandas as pd

server = Flask(__name__)
app = dash.Dash(__name__, server=server)

app = dash.Dash(meta_tags=[
    {
        'name': 'description',
        'content': 'Interactive charts displaying GVA statistics for DCMS sectors.'
    },
])


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

gva_creative = make_table('Creative Industries')
gva_digital = make_table('Digital Sector')
gva_culture = make_table('Cultural Sector')
gva_current = make_table('All')
gva_current_indexed = make_table('All', indexed=True)


#https://github.com/DCMSstats/images/raw/master/logo-gov-white.png
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

This tool shows GVA for DCMS sectors. It is based on [National Accounts](https://www.ons.gov.uk/economy/nationalaccounts) data.

To help ensure the information in this dashboard is transparent, the data used is pulled directly from [gov.uk/government/statistical-data-sets/museums-and-galleries-monthly-visits](https://www.gov.uk/government/statistical-data-sets/museums-and-galleries-monthly-visits) which has information about the data and a [preview](https://www.gov.uk/government/uploads/system/uploads/attachment_data/file/731313/Monthly_museums_and_galleries_June_2018.csv/preview), and the dashboard's [source code](https://github.com/DCMSstats/museum-visits-interactive-dashboard) is [open source](https://www.gov.uk/service-manual/technology/making-source-code-open-and-reusable) with an [Open Government Licence](http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
            ''')], id='preamble', className='markdown mysection'),

html.Section([

html.Div([
dcc.Dropdown(
    id='breakdown-dropdown',
    className='mydropdown',
    options=[{'label': i, 'value': i} for i in ['All', 'Creative Industries', 'Digital Sector', 'Cultural Sector']],
    value='Creative Industries'
),
dcc.Dropdown(
    id='indexed-dropdown',
    className='mydropdown',
    options=[{'label': i, 'value': i} for i in ['Actual', 'Indexed']],
    value='Actual'
),
dcc.Dropdown(
    id='cvm-dropdown',
    className='mydropdown',
    options=[{'label': i, 'value': i} for i in ['Current Price', 'Chained Volume Measure']],
    value='Current Price'
),
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


@app.callback(Output('ts-graph', 'figure'), [Input('breakdown-dropdown', 'value'), Input('indexed-dropdown', 'value')])
def update_graph(breakdown, indexed):
    indexed_bool = False
    if indexed == 'Indexed':
        indexed_bool = True
    tb = make_table(breakdown, indexed_bool)
    traces = []
    for i in tb.index:
        traces.append(go.Scatter(
            x=list(tb.columns),
            y=list(tb.loc[i, :].values),
            mode = 'lines+markers',
            name=i
        ))    
    
    layout = dict(
        #title='Compare visits between museums',
        margin = dict(l=30, r=0, t=30, b=30, pad=0),
    )
    return dict(data=traces, layout=layout)
    
    
if __name__ == '__main__':
    app.run_server(debug=True)