import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
from os.path import isfile
import plotly.io as pio
import plotly.graph_objs as go
from datetime import datetime, timedelta


baseURL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"
fileNamePickle = "allData.pkl"
fileNamePickles = "world.pkl"

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

tickFont = {'size':12, 'color':"rgb(30,30,30)", 'family':"Courier New, monospace"}
def prepare_daily_report():

    current_date = (datetime.today() - timedelta(days=1)).strftime('%m-%d-%Y')

    df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/' + current_date + '.csv')
    df_country = df.groupby(['Country_Region']).sum().reset_index()
    df_country.replace('US', 'United States', inplace=True)
    df_country.replace(0, 1, inplace=True)
    
    code_df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_world_gdp_with_codes.csv')
    df_country_code = df_country.merge(code_df, left_on='Country_Region', right_on='COUNTRY', how='left')

    df_country_code.loc[df_country_code.Country_Region == 'Congo (Kinshasa)', 'CODE'] = 'COD'
    df_country_code.loc[df_country_code.Country_Region == 'Congo (Brazzaville)', 'CODE'] = 'COG'
    
    return(df_country_code)
	
def loadData_GLOB(fileName, columnName): 
    agg_dict = { columnName:sum, 'Lat':np.median, 'Long':np.median }
    data = pd.read_csv(baseURL + fileName) \
             .rename(columns={ 'Country/Region':'Country' }) \
             .melt(id_vars=['Country', 'Province/State', 'Lat', 'Long'], var_name='date', value_name=columnName) \
             .astype({'date':'datetime64[ns]', columnName:'Int64'}, errors='ignore')
    ## Extract chinese provinces separately.
    data_CHI = data[data.Country == 'China']
    data = data.groupby(['Country', 'date']).agg(agg_dict).reset_index()
    data['Province/State'] = '<all>'
    return pd.concat([data, data_CHI])

def loadData_US(fileName, columnName): 
    id_vars=['Country', 'Province/State', 'Lat', 'Long']
    agg_dict = { columnName:sum, 'Lat':np.median, 'Long':np.median }
    data = data = pd.read_csv(baseURL + fileName).iloc[:, 6:]
    if 'Population' in data.columns:
        data = data.drop('Population', axis=1)
    data = data \
             .drop('Combined_Key', axis=1) \
             .rename(columns={ 'Country_Region':'Country', 'Province_State':'Province/State', 'Long_':'Long' }) \
             .melt(id_vars=id_vars, var_name='date', value_name=columnName) \
             .astype({'date':'datetime64[ns]', columnName:'Int64'}, errors='ignore') \
             .groupby(['Country', 'Province/State', 'date']).agg(agg_dict).reset_index()
    return data

def simple_moving_average(df, len=7):
    return df.rolling(len).mean()

def refreshData():
    data_GLOB = loadData_GLOB("time_series_covid19_confirmed_global.csv", "CumConfirmed") \
        .merge(loadData_GLOB("time_series_covid19_deaths_global.csv", "CumDeaths"))\
		.merge(loadData_GLOB("time_series_covid19_recovered_global.csv", "CumRecovered"))
    data_GLOB.to_pickle(fileNamePickles)
    
    data_US = loadData_US("time_series_covid19_confirmed_US.csv", "CumConfirmed") \
        .merge(loadData_US("time_series_covid19_deaths_US.csv", "CumDeaths"))
		
    data = pd.concat([data_GLOB, data_US])
    data.to_pickle(fileNamePickle)
    return data

def allData():
    if not isfile(fileNamePickle):
        refreshData()
    allData = pd.read_pickle(fileNamePickle)
    return allData
def allDataw():
    if not isfile(fileNamePickles):
        refreshData()
    allData = pd.read_pickle(fileNamePickles)
    return allData

def generate_table(dataframe, max_rows=500):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

abc=allDataw()
data0=abc.groupby('Country', as_index=False).agg({'CumConfirmed': 'max', 'CumDeaths': 'max', 'CumRecovered': 'max'})
df = pd.DataFrame(data0).reset_index()
stt = [i for i in range(1,len(df)+1)]
df['Order'] = stt
df= df[['Order','Country','CumConfirmed','CumDeaths','CumRecovered']]

dft=df.nlargest(20,'CumDeaths')
dft.sort_values(by=['CumConfirmed','CumDeaths'], inplace=True,ascending=[False, False])
stt = [i for i in range(1,21)]
dft['Order'] = stt
dft= dft[['Order','Country','CumConfirmed','CumDeaths','CumRecovered']]

dfb=df.nsmallest(20,'CumDeaths')
dfb.sort_values(by=['CumConfirmed','CumDeaths'], inplace=True, ascending=[True, False])
dfb['Order'] = stt
dfb= dfb[['Order','Country','CumConfirmed','CumDeaths','CumRecovered']]

countries = list(allData()['Country'].unique())
countries.insert(0, '<all>')
countries.sort()

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

## App title, keywords and tracking tag (optional).
app.index_string = """<!DOCTYPE html>
<html>
    <head>
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=UA-40117610-2"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());

          gtag('config', 'UA-40117610-2');
        </script>
		<meta name="google-site-verification" content="H8mgS9So3FfFTxD3Sh9dRie1Bgd2Z5ntZ7P0nHwR8go" />
        <meta name="keywords" content="COVID-19,Coronavirus,Chinavirus,Cases,Statistics">
        <title>COVID-19 Statistics</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
	{%css%}
        {%app_entry%}
        	
        <footer>
			{%config%}
            {%scripts%}
            {%renderer%}
        <div class="footer-copyright text-center py-3">© 2020 Copyright: <a href="http://tnmthai.com/"> TNMThai</a>
                    </div>
       </footer>	
    </body>
</html>"""

app.layout = html.Div(
    style={ 'font-family':"Courier New, monospace" },
    children=[
        html.H1('COVID-19 Statistics'),
		html.Div(className="row", children=[
            html.Div(className="four columns", children=[
                html.H5('Country'),
                dcc.Dropdown(
                    id='country',
                    options=[{'label':c, 'value':c} for c in countries],
                    value='<all>'),
                html.H5('State / Province'),
                dcc.Dropdown(
                    id='state'  )
            ]),
            
            html.Div(className="four columns", children=[
                html.H5('Summary:'),
                html.Div(id='s1'),
                html.Div(id='s2'),
                html.Div(id='s3'),
                html.Div(id='s4'),
                html.Div(id='s5'),
                html.Div(id='s7'),
                html.Div(id='s6')
            ]),
            html.Div(className="four columns", children=[
                html.H5('Options:'),
                dcc.Checklist(
                    id='metrics',
                    options=[{'label':m, 'value':m} for m in ['Confirmed', 'Deaths']],
                    value=['Confirmed', 'Deaths']
                )
            ])
        ]),
        dcc.Graph(
            id="plot_new_metrics",
            config={ 'displayModeBar': False }
        ),             
        dcc.Graph(
            id="plot_cum_metrics",
            config={ 'displayModeBar': False }
        ),     

       html.Div([html.Div([html.H1("Covid-19 Map")],
                                style={'textAlign': "center", "padding-bottom": "30"}
                               ),
                       html.Div([html.Span("Metric to display : ", className="six columns",
                                           style={"text-align": "right", "width": "80%", "padding-top": 10}),
                                 dcc.Dropdown(id="value-selected", value='Confirmed',
                                              options=[{'label': "Confirmed ", 'value': 'Confirmed'},
                                                       {'label': "Recovered ", 'value': 'Recovered'},
                                                       {'label': "Deaths ", 'value': 'Deaths'},
                                                       {'label': "Active ", 'value': 'Active'}],
                                              style={"display": "block", "margin-left": "auto", "margin-right": "auto",
                                                     "width": "90%"},
                                              className="six columns")], className="row"),
                       dcc.Graph(id="my-graph")
                       ], className="container"),

                
	html.Div(className="table", children=[
             html.H3(children='Most CumDeaths'),             
             generate_table(dft),
	     html.H3(children='Least CumDeaths'),
             generate_table(dfb),
	     html.H3(children='All over the World'),
             generate_table(df)	,
        ]),
		dcc.Interval(
            id='interval-component',
            interval=1500*1000, # Refresh data 25m.
            n_intervals=0
        ),
		html.H5('(Data source: The Johns Hopkins Center(JHU/CSSE))'),
		html.H5('Code: Python; Host: Heroku')
    ])

@app.callback(
    [Output('state', 'options'), Output('state', 'value')],
    [Input('country', 'value')]
)
def update_states(country):
    d = allDataw()
    states = list(d.loc[d['Country'] == country]['Province/State'].unique())
    states.insert(0, '<all>')
    states.sort()
    state_options = [{'label':s, 'value':s} for s in states]
    state_value = state_options[0]['value']
    return state_options, state_value

def filtered_data(country, state):
    dw = allDataw()
    if country != '<all>':
        data = dw.loc[dw['Country'] == country]  
        if state == '<all>':
            data = data.drop('Province/State', axis=1).groupby("date").sum().reset_index()
        else:
            data = data.loc[data['Province/State'] == state]	
    else:
        data = dw.drop('Province/State', axis=1).groupby("date").sum().reset_index()
	
    newCases = data.select_dtypes(include='Int64').diff().fillna(0)
    newCases.columns = [column.replace('Cum', 'New') for column in newCases.columns]
    data = data.join(newCases)
    data['dateStr'] = data['date'].dt.strftime('%b %d, %Y')
    data['NewDeathsSMA7'] = simple_moving_average(data.NewDeaths, len=7)
    data['NewConfirmedSMA7'] = simple_moving_average(data.NewConfirmed, len=7)
    return data

def add_trend_lines(figure, data, metrics, prefix):
    if prefix == 'New':
        for metric in metrics:
            figure.add_trace(
                go.Scatter(
                    x=data.date, y=data[prefix + metric + 'SMA7'], 
                    mode='lines', line=dict(
                        width=3, color='rgb(200,30,30)' if metric == 'Deaths' else 'rgb(100,140,240)'
                    ),
                    name='Rolling 7-Day Average of Deaths' if metric == 'Deaths' \
                        else 'Rolling 7-Day Average of Confirmed'
                )
            )

def barchart(data, metrics, prefix="", yaxisTitle=""):
    
    figure = go.Figure(data=[
        go.Bar( 
            name=metric, x=data.date, y=data[prefix + metric],
            marker_line_color='rgb(0,0,0)', marker_line_width=1,
            marker_color={ 'Deaths':'rgb(200,30,30)', 'Confirmed':'rgb(100,140,240)'}[metric]
        ) for metric in metrics
    ])
    	
    add_trend_lines(figure, data, metrics, prefix)
	
    figure.update_layout( 
              barmode='group', legend=dict(x=.05, y=0.95, font={'size':15}, bgcolor='rgba(240,240,240,0.5)'), 
              plot_bgcolor='#FFFFFF', font=tickFont) \
          .update_xaxes( 
              title="", tickangle=-90, type='category', showgrid=True, gridcolor='#DDDDDD', 
              tickfont=tickFont, ticktext=data.dateStr, tickvals=data.date) \
          .update_yaxes(
              title=yaxisTitle, showgrid=True, gridcolor='#DDDDDD')
    
    
    return figure

@app.callback(
    [Output('plot_new_metrics', 'figure'), Output('plot_cum_metrics', 'figure'),Output('s1', 'children'),Output('s2', 'children'),Output('s3', 'children'),Output('s4', 'children'),Output('s5', 'children'),Output('s6', 'children'),Output('s7', 'children')], 
    [Input('country', 'value'), Input('state', 'value'), Input('metrics', 'value'), Input('interval-component', 'n_intervals')]
)
def update_plots(country, state, metrics, n):
    refreshData()
    data = filtered_data(country, state)
    barchart_new = barchart(data, metrics, prefix="New", yaxisTitle="New Cases per Day")
    barchart_cum = barchart(data, metrics, prefix="Cum", yaxisTitle="Cumulated Cases")
    
    d1=data['dateStr'][len(data)-1]
    d2=data['CumConfirmed'][len(data)-1]
    d3=data['CumDeaths'][len(data)-1]
    d4=data['NewConfirmed'][len(data)-1]
    d5=data['NewDeaths'][len(data)-1]
    d7=data['CumRecovered'][len(data)-1]
    
    abc=allDataw()
    data0=abc.groupby('Country', as_index=False).agg({'CumConfirmed': 'max', 'CumDeaths': 'max'})
    df = pd.DataFrame(data0).reset_index()
    d6 = len(df)

    
    
       
    return barchart_new, barchart_cum,'Date: "{!s}"'.format(d1).replace('"', ""),'Total cases: "{:,}"'.format(d2).replace('"', ""),'Total deaths: "{:,}"'.format(d3).replace('"', ""),'Total new cases: "{:,}"'.format(d4).replace('"', ""),'Total new deaths: "{:,}"'.format(d5).replace('"', ""),'Total countries: "{:,}"'.format(d6).replace('"', ""),'Total recovered cases: "{:,}"'.format(d7).replace('"', "")


	
@app.callback(
    dash.dependencies.Output("my-graph", "figure"),
    [dash.dependencies.Input("value-selected", "value")])
	
def update_figure(selected):
    #dff = prepare_confirmed_data()

    dff = prepare_daily_report()
    dff['hover_text'] = dff["Country_Region"] + ": " + dff[selected].apply(str)

    trace = go.Choropleth(locations=dff['CODE'],z=np.log(dff[selected]),
                          text=dff['hover_text'],
                          hoverinfo="text",
                          marker_line_color='white',
                          autocolorscale=False,
                          reversescale=True,
                          colorscale="RdBu",marker={'line': {'color': 'rgb(180,180,180)','width': 0.5}},
                          colorbar={"thickness": 10,"len": 0.3,"x": 0.9,"y": 0.7,
                                    'title': {"text": 'persons', "side": "bottom"},
                                    'tickvals': [ 2, 10],
                                    'ticktext': ['100', '100K', '1M']})   
    return {"data": [trace],
            "layout": go.Layout(height=800,geo={'showframe': False,'showcoastlines': False,
                                                                      'projection': {'type': "miller"}})}	
	
server = app.server

if __name__ == '__main__':
    app.run_server(host="0.0.0.0")
