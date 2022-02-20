from datetime import date

import pandas as pd
from django.shortcuts import render
from gcampus.analysis.dash_apps.Example_Measurement import create_graph, app
from gcampus.core.models import ParameterType, Measurement


def analysis(requests):
    return render(requests, "gcampusanalysis/analysis.html")


def analysis_measurement(requests):
    parameter_types_names = [i.name for i in list(ParameterType.objects.all())]
    parameter_types = list(ParameterType.objects.all())

    water_names = list(
        set(Measurement.objects.values_list("water_name", flat=True).distinct())
    )

    months = (
        pd.date_range("2020-1-10", date.today().strftime("%Y-%m-%d"), freq="MS")
        .strftime("%Y-%m")
        .tolist()
    )

    create_graph(app, parameter_types_names, parameter_types, water_names, months)

    return render(requests, "gcampusanalysis/analysis_measurement.html")
