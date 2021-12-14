import pandas as pd
import datetime



from gcampus.core.models import Parameter, Measurement

from django.contrib.gis.geos import Point

def remove_one_day(date: str, date_format: str):

    date = datetime.datetime.strptime(date, date_format)
    time_delta = datetime.timedelta(days=-1)
    max_time = datetime.datetime.strftime((date + time_delta), date_format)
    return max_time


def add_one_day(date: str, date_format: str):
    date = datetime.datetime.strptime(date, date_format)
    time_delta = datetime.timedelta(days=1)
    max_time = datetime.datetime.strftime((date + time_delta), date_format)
    return max_time


def database_query_for_plot(water_name, parameter_type, time, course=None):
    if course:
        query = Parameter.objects.filter(parameter_type=parameter_type, measurement__water_name=water_name,
                                         measurement__token__parent_token=course.token)
    else:
        query = Parameter.objects.filter(parameter_type=parameter_type, measurement__water_name=water_name)
    # TODO Dirty, fix
    parameter_measured_list = []
    for item in query:
        parameter_measured = Measurement.objects.get(parameters=item).time
        parameter_measured_list.append(parameter_measured.strftime("%Y-%m-%d"))

    values = [item.value for item in query]
    return parameter_measured_list, values



