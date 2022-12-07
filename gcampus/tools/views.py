import math

from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, DetailView, TemplateView

from gcampus.core.models import ParameterType
from gcampus.tools.models import Calibration, MeasurementKit
from gcampus.core.views.base import TitleMixin


class ToolsOverView(TitleMixin, TemplateView):
    title = _("Tools")
    template_name = "gcampustools/tools.html"


class MeasurementKitOverView(TitleMixin, ListView):
    title = _("Measurement Kits")
    template_name = "gcampustools/measurement_kit_overview.html"
    model = MeasurementKit

    def get_context_data(self, **kwargs):
        available_kits = MeasurementKit.objects.filter(
            calibrations__isnull=False
        ).distinct()
        kwargs["kits"] = available_kits
        kwargs["row_num"] = math.ceil(len(available_kits) / 3)
        kwargs["kits_num"] = len(available_kits)
        return super(MeasurementKitOverView, self).get_context_data(**kwargs)


class ODConverterOverView(TitleMixin, ListView):
    title = _("Optical Density Converter")
    template_name = "gcampustools/od_converter_overview.html"
    model = ParameterType

    def get_context_data(self, **kwargs):
        available_parameters = ParameterType.objects.filter(
            calibrations__isnull=False,
            calibrations__measurement_kit=self.kwargs.get("pk_kit"),
        ).distinct()
        kwargs["parameters"] = available_parameters
        kwargs["row_num"] = math.ceil(len(available_parameters) / 3)
        kwargs["param_num"] = len(available_parameters)
        kwargs["pk_kit"] = self.kwargs.get("pk_kit")
        return super(ODConverterOverView, self).get_context_data(**kwargs)


class ODConverterDetailView(TitleMixin, DetailView):
    title = _("Optical Density Converter")
    template_name = "gcampustools/od_converter_detail.html"
    model = ParameterType
    context_object_name = "parameter"

    def get_context_data(self, **kwargs):
        kwargs["calibrations"] = Calibration.objects.filter(
            parameter_type=self.object,
            measurement_kit=self.kwargs.get("pk_kit"),
        ).all()
        kwargs["pk_kit"] = self.kwargs.get("pk_kit")
        return super(ODConverterDetailView, self).get_context_data(**kwargs)
