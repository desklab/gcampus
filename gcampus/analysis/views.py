import math

from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView

from gcampus.core.models import ParameterType, Calibration
from gcampus.core.views.base import TitleMixin


class ODConverterOverView(TitleMixin, ListView):
    title = _("Optical Density Converter")
    template_name = "gcampusanalysis/od_converter_overview.html"
    model = ParameterType
    context_object_name = "parameter"

    def get_context_data(self, **kwargs):
        kwargs["row_num"] = math.ceil(len(ParameterType.objects.all()) / 3)
        kwargs["param_num"] = len(ParameterType.objects.all())
        return super(ODConverterOverView, self).get_context_data(**kwargs)


class ODConverterDetailView(TitleMixin, DetailView):
    title = _("Optical Density Converter")
    template_name = "gcampusanalysis/od_converter_detail.html"
    model = ParameterType
    context_object_name = "parameter"

    def get_context_data(self, **kwargs):
        kwargs["calibrations"] = Calibration.objects.all().filter(
            calibration_parameter_type=self.object
        )
        return super(ODConverterDetailView, self).get_context_data(**kwargs)
