import pandas as pd
import numpy as np



from gcampus.core.models import Parameter, Measurement

from django.contrib.gis.geos import Point


def database_query_for_plot(water_name, parameter_type, time):
    query = Parameter.objects.filter(parameter_type=parameter_type, measurement__water_name=water_name)
    # TODO Dirty, fix
    parameter_measured_list = []
    for item in query:
        parameter_measured = Measurement.objects.get(parameters=item).time
        parameter_measured_list.append(parameter_measured.strftime("%Y-%m-%d"))

    values = [item.value for item in query]
    return parameter_measured_list, values


def create_df_location(location: Point, radius: int):
    df = pd.DataFrame(list(Parameter.objects.filter(location__distance_lte=(location, radius)).values()))
    return df
