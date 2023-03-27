import math

from django.shortcuts import get_object_or_404
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

    def get_queryset(self):
        self.queryset = MeasurementKit.objects.filter(
            calibrations__isnull=False
        ).distinct()
        return super(MeasurementKitOverView, self).get_queryset()


class ODConverterOverView(TitleMixin, ListView):
    title = _("Optical Density Converter")
    template_name = "gcampustools/od_converter_overview.html"
    model = ParameterType

    def get_queryset(self):
        self.queryset = ParameterType.objects.filter(
            calibrations__isnull=False,
            calibrations__measurement_kit=self.kwargs.get("pk_kit"),
        ).distinct()
        return super(ODConverterOverView, self).get_queryset()

    def get_context_data(self, **kwargs):
        kwargs["row_num"] = math.ceil(len(self.queryset) / 3)
        kwargs["param_num"] = len(self.queryset)
        kwargs["kit"] = get_object_or_404(MeasurementKit, pk=self.kwargs.get("pk_kit"))
        return super(ODConverterOverView, self).get_context_data(**kwargs)


class ODConverterDetailView(TitleMixin, DetailView):
    title = _("Optical Density Converter")
    template_name = "gcampustools/od_converter_detail.html"
    model = ParameterType
    context_object_name = "parameter"

    def get_context_data(self, **kwargs):
        kwargs["calibrations"] = (
            Calibration.objects.filter(
                parameter_type=self.object,
                measurement_kit=self.kwargs.get("pk_kit"),
            )
            .order_by("pk")
            .all()
        )
        kwargs["kit"] = get_object_or_404(MeasurementKit, pk=self.kwargs.get("pk_kit"))
        return super(ODConverterDetailView, self).get_context_data(**kwargs)
