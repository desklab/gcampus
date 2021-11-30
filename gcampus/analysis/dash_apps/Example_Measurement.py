import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
from gcampus.analysis.util import database_query_for_plot

import pandas as pd
from django_plotly_dash import DjangoDash

from gcampus.core.models import ParameterType, Measurement

app = DjangoDash("ExampleMeasurement")

parameter_types_names = [i.name for i in list(ParameterType.objects.all())]
parameter_types = list(ParameterType.objects.all())

water_names = list(set(Measurement.objects.values_list('water_name', flat=True).distinct()))

app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='parameter_type',
                options=[{'label': i, 'value': i} for i, j in zip(parameter_types_names, parameter_types)],
                value=parameter_types[0].name
            ),
            dcc.RadioItems(
                id='yaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='water_name',
                options=[{'label': i, 'value': i} for i in water_names],
                value=water_names[0]
            ),

        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),

    ]),
    dcc.Graph(id='indicator-graphic'),
])


@app.callback(
    Output('indicator-graphic', 'figure'),
    Input('parameter_type', 'value'),
    Input('water_name', 'value'),
    Input('yaxis-type', 'value'))
def update_graph(parameter_type, water_name, yaxis_type):
    if not isinstance(parameter_type, ParameterType):
        parameter_type = ParameterType.objects.get(name=parameter_type)

    x, y = database_query_for_plot(water_name, parameter_type, 0)

    df = pd.DataFrame(list(zip(x, y)), columns =["Time", "Values"])
    fig = px.scatter(df, x="Time", y="Values")

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    fig.update_xaxes()

    fig.update_yaxes(title=parameter_type.name,
                     type='linear' if yaxis_type == 'Linear' else 'log')

    return fig
