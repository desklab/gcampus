from gcampus.settings.analysis import LIMITS, PLOT_TYPES, SCATTER_PLOT, HISTOGRAM, BOXPLOT
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
from gcampus.analysis.util import database_query_for_plot, remove_one_day, add_one_day

from datetime import date

import pandas as pd
from django_plotly_dash import DjangoDash

from gcampus.core.models import ParameterType, Measurement

app = DjangoDash("ExampleMeasurement")

parameter_types_names = [i.name for i in list(ParameterType.objects.all())]
parameter_types = list(ParameterType.objects.all())

water_names = list(set(Measurement.objects.values_list('water_name', flat=True).distinct()))

months = pd.date_range('2020-1-10', date.today().strftime("%Y-%m-%d"),
              freq='MS').strftime("%Y-%m").tolist()

app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='parameter_type',
                options=[{'label': i, 'value': i} for i, j in zip(parameter_types_names, parameter_types)],
                # if statement needed for tests, error if parameter_types is empty
                value=parameter_types[0].name if parameter_types else None
            ),
            dcc.RadioItems(
                id='plot-type',
                options=[{'label': i, 'value': i} for i in PLOT_TYPES],
                value='Scatter',
                labelStyle={'display': 'inline-block'}
            ),
            dcc.RadioItems(
                id='limits',
                options=[{'label': i, 'value': j} for i, j in zip(["Show Limits", "Hide Limits"], [1, 0])],
                value=1,
                labelStyle={'display': 'inline-block'}
            )
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='water_name',
                options=[{'label': i, 'value': i} for i in water_names],
                # if statement needed for tests, error if water_names is empty
                value=water_names[0] if water_names else None
            ),

        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),

    ]),
    dcc.Graph(id='indicator-graphic'),
    dcc.Slider(
        id='year--slider',
        min=months[0],
        max=months[-1],
        value=months[0],
        marks={str(month): str(month) for month in months},
        step=None
    ),
])


@app.callback(
    Output('indicator-graphic', 'figure'),
    Input('parameter_type', 'value'),
    Input('water_name', 'value'),
    Input('plot-type', 'value'),
    Input('limits', 'value'),
    Input('year--slider', 'value'))
def update_graph(parameter_type, water_name, plot_type, show_limit, slider):
    if not isinstance(parameter_type, ParameterType):
        parameter_type = ParameterType.objects.get(name=parameter_type)

    x, y = database_query_for_plot(water_name, parameter_type, 0)

    df = pd.DataFrame(list(zip(x, y)), columns=["Time", "Values"])

    if df["Values"].size == 0:
        fig = px.scatter(df, x="Time", y="Values")

        fig.update_xaxes()

        fig.update_yaxes(title=parameter_type.name)

        return fig

    if plot_type == SCATTER_PLOT:
        fig = px.scatter(df, x="Time", y="Values")
        if parameter_type.id in LIMITS.keys() and show_limit:
            limit = LIMITS[parameter_type.id]

            max_time = max(df["Time"])
            max_time = add_one_day(max_time, "%Y-%m-%d")

            min_time = min(df["Time"])
            min_time = remove_one_day(min_time, "%Y-%m-%d")

            fig.add_shape(type='line',
                          x0=min_time,
                          y0=limit,
                          x1=max_time,
                          y1=limit,
                          line=dict(color='Red', ),
                          xref='x',
                          yref='y'
                          )
            fig.update_layout(margin={'l': 0, 'b': 40, 't': 10, 'r': 0}, hovermode='closest',
                              yaxis_range=[min(min(df["Values"]), limit) - 5, max(max(df["Values"]), limit) + 5],
                              xaxis_range=[min_time, max_time])
        else:
            fig.update_layout(margin={'l': 0, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    elif plot_type == HISTOGRAM:
        fig = px.histogram(df, x="Values")

    elif plot_type == BOXPLOT:
        fig = px.box(df, y="Values")

    fig.update_xaxes()

    fig.update_yaxes(title=parameter_type.name)

    return fig
