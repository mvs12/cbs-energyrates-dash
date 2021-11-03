import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import cbsodata


# Retrieve data from CBS
# Average energy prices for consumers 84672ENG
def retreive_data_cbs(data):
    df = pd.DataFrame(cbsodata.get_data(data))
    return df


df = retreive_data_cbs('84672ENG')


# Filter data with values including VAT and excluding Full Years
df = df[df['VAT'] == 'Including VAT']
df = df[(df['Period'] != '2018') &
        (df['Period'] != '2019') &
        (df['Period'] != '2020') &
        (df['Period'] != '2021')]


# Calculate prices
df['Gas EUR per m3'] = df['VariableDeliveryRate_3'] + df['ODETaxEnvironmentalTaxesAct_4'] + df['EnergyTax_5']
df['Electricity EUR per kWh'] = df['VariableDeliveryRate_8'] + df['ODETaxEnvironmentalTaxesAct_9'] + df['EnergyTax_10']


# Create Dimensions
df['Period'] = pd.to_datetime(df['Period'], format='%Y %B')


# Create Measurements
gas = df['Gas EUR per m3'].tolist()
electricity = df['Electricity EUR per kWh'].tolist()


# Create app layout
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server


# the style arguments for the sidebar.
SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '15%',
    'padding': '20px 10px',
    'background-color': '#ECF0F1'
}

# the style arguments for the main content page.
CONTENT_STYLE = {
    'margin-left': '25%',
    'margin-right': '5%',
    'padding': '20px 10p'
}

# Controls
controls = dbc.Form(
    [
        html.Br(),
        dcc.Markdown("Select year:"),
        dcc.Dropdown(
            id='dropdown_1',
            options=[
                {'label': '2018', 'value': 2018},
                {'label': '2019', 'value': 2019},
                {'label': '2020', 'value': 2020},
                {'label': '2021', 'value': 2021}
            ],
            value=[2018, 2019, 2020, 2021],
            multi=True
        ),
        html.Br()
    ]
)

sidebar = html.Div(
    [
        html.H1(["Follow energy prices for consumers in the Netherlands"]),
        html.Br(),
        dcc.Markdown("""
                    Follow Dutch energy prices from 2018 until 2021, monthly published by CBS. Prices are variable
                     rates, including VAT and including surcharge for renewable energy. Prices are excluded Transport
                      Rates and Fixed Rates.
                    """),
        dcc.Markdown("""
                        Source: [CBS Open data StatLine](https://opendata.cbs.nl/statline/)
                        
                        Sourcecode: [Github](https://github.com/mvs12/cbs-energyrates-streamlit)
                        """),
        controls
    ],
    # style=SIDEBAR_STYLE,
)

content_first_row = dbc.Row([
    dbc.Col(
        html.Div([
            html.H4(dbc.Badge(id='regions_text', color="primary")),
            dcc.Graph(id='graph_1')
        ]), md=12, xs=12)
])

content = html.Div(
    [
        html.Br(),
        html.Br(),
        content_first_row,
    ],
    # style=CONTENT_STYLE
)


app.layout = html.Div(dbc.Container([sidebar, content]))


# Create graph
@app.callback(
    Output('graph_1', 'figure'),
    # Output('regions_text', 'children'),
    Input('dropdown_1', 'value'))
def update_figure(years):
    filtered_df = df[df['Period'].dt.year.isin(years)]

    fig = px.line(filtered_df, x="Period", y=["Gas EUR per m3", "Electricity EUR per kWh"],
                    line_shape="spline",
                    template="simple_white",
                    labels={"Period": 'Year', "Gas EUR per m3": 'Gas EUR per m3'},
                    title="Average variable energy prices for consumers in The Netherlands"
                    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
