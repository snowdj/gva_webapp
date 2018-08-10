import dash
import dash_core_components as dcc
import dash_html_components as html
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



app.layout = html.Div([
    html.Div(
        className="app-header",
        children=[
            html.Div('Plotly Dash', className="app-header--title")
        ]
    ),
    html.Div(
        children=html.Div([
            html.H5('Overview'),
            html.Div('''
                This is an example of a simple Dash app with
                local, customized CSS.
            ''')
        ])
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)