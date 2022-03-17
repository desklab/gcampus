import csv

from io import StringIO

from django.http import StreamingHttpResponse
from django.utils.translation import gettext_lazy as _

from gcampus.core.filters import MeasurementFilterSet
from gcampus.core.models.measurement import Measurement, ParameterType


def get_headers():
    Initial_header = [_("ID"), _("Name"), _("Location Name"), _("Water Name"), _("Time")]
    all_parameters = ParameterType.objects.values_list("name", "pk").order_by("pk").all()
    for parameter in all_parameters:
        Initial_header.append(parameter[0])
    return Initial_header


def stream(rows, writer, buffer_):
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
        buffer_.seek(0)
        data = buffer_.read()
        buffer_.seek(0)
        buffer_.truncate()
        yield data

def replace_none_with_empty_str(some_dict):
    return {k: ('' if v is None else v) for k, v in some_dict.items()}


def generator(queryset, parameter_type):
    # Desired values in csv
    values = queryset.values("pk", "name", "location_name",
                             "water_name", "time", "parameters__value",
                             "parameters__parameter_type__name"
                             ).order_by("pk").all()
    current = None
    for m in values:
        m = replace_none_with_empty_str(m)
        if current is not None and current.get("id") != m["pk"]:
            yield current
            current = None
        if current is None:
            current = {_("ID"): m["pk"],
                       _("Name"): m["name"],
                       _("Location Name"): m["location_name"],
                       _("Water Name"): m["water_name"],
                       _("Time"): m["time"]}
            current.update({
                pk: "" for pk in parameter_type
            })
        if m["parameters__value"] != "":
            current[m["parameters__parameter_type__name"]] = m["parameters__value"]
    yield current

def filter_csv_download(request):
    """A view that streams the current filtered measurements to a csv file"""

    # Get and Set current filer
    set_filter = MeasurementFilterSet(
        request.GET, queryset=Measurement.objects.all(), request=request
    )
    queryset = set_filter.qs

    # Get a list of all parameters
    parameter_types = ParameterType.objects.values_list("name", flat=True).order_by("pk").all()

    # Set up csv writer
    buffer_ = StringIO()
    header = get_headers()
    writer = csv.DictWriter(buffer_,
                        delimiter=',',
                        quoting=csv.QUOTE_ALL,
                        fieldnames=header)
    # create generator that yields single measurements
    generate_csv = generator(queryset, parameter_types)
    filename = _("gcampus_measurements.csv")
    return StreamingHttpResponse(stream(generate_csv, writer, buffer_), content_type='text/csv',
                                 headers={'Content-Disposition': f'attachment; filename={filename}'}, )
