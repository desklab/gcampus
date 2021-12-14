from gcampus.settings.analysis import PLOT_TYPES, SCATTER_PLOT, HISTOGRAM, BOXPLOT
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
from gcampus.analysis.util import database_query_for_plot, remove_one_day, add_one_day


import pandas as pd
from django_plotly_dash import DjangoDash

from gcampus.core.models import ParameterType, Limit

app = DjangoDash("ExampleMeasurement")


def create_graph(app, parameter_types_names, parameter_types, water_names, months):
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
    return app


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
    limits = Limit.objects.filter(parameter_limit=parameter_type)

    x, y = database_query_for_plot(water_name, parameter_type, 0)

    df = pd.DataFrame(list(zip(x, y)), columns=["Time", "Values"])

    if df["Values"].size == 0:
        fig = px.scatter(df, x="Time", y="Values")

        fig.update_xaxes()

        fig.update_yaxes(title=parameter_type.name)

        return fig

    if plot_type == SCATTER_PLOT:
        fig = px.scatter(df, x="Time", y="Values")
        if limits and show_limit:

            for limit in limits:
                fig.add_hline(y=limit.limit_value, line_color=limit.graph_color, line_dash="dash", name=limit.limit_type)

        fig.update_layout(margin={'l': 0, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    elif plot_type == HISTOGRAM:
        fig = px.histogram(df, x="Values")

    elif plot_type == BOXPLOT:
        fig = px.box(df, y="Values")

    fig.update_xaxes()

    fig.update_yaxes(title=parameter_type.name)

    return fig
