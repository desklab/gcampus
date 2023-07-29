#  Copyright (C) 2023 desklab gUG (haftungsbeschränkt)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

__all__ = [
    "ToolsOverView",
    "MeasurementKitOverView",
    "ODConverterOverView",
    "ODConverterDetailView",
]

import math

from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy
from django.views.generic import ListView, DetailView, TemplateView

from gcampus.core.models import ParameterType
from gcampus.core.views.base import TitleMixin
from gcampus.tools.models import Calibration, MeasurementKit


class ToolsOverView(TitleMixin, TemplateView):
    title = gettext_lazy("Tools")
    template_name = "gcampustools/tools.html"


class MeasurementKitOverView(TitleMixin, ListView):
    title = gettext_lazy("Measurement Kits")
    template_name = "gcampustools/measurement_kit_overview.html"
    model = MeasurementKit
    queryset = MeasurementKit.objects.filter(calibrations__isnull=False).distinct()


class ODConverterOverView(TitleMixin, ListView):
    title = gettext_lazy("Optical Density Converter")
    template_name = "gcampustools/od_converter_overview.html"
    model = ParameterType
    kit: MeasurementKit

    def get_title(self) -> str:
        return f"{self.title} ({self.kit.short_name})"

    def get_queryset(self):
        self.kit = get_object_or_404(MeasurementKit, pk=self.kwargs.get("pk_kit"))
        self.queryset = ParameterType.objects.filter(
            calibrations__isnull=False,
            calibrations__measurement_kit=self.kit,
        ).distinct()
        return super(ODConverterOverView, self).get_queryset()

    def get_context_data(self, **kwargs):
        kwargs["row_num"] = math.ceil(len(self.queryset) / 3)
        kwargs["param_num"] = len(self.queryset)
        kwargs["kit"] = self.kit
        return super(ODConverterOverView, self).get_context_data(**kwargs)


class ODConverterDetailView(TitleMixin, DetailView):
    title = gettext_lazy("Optical Density Converter")
    template_name = "gcampustools/od_converter_detail.html"
    model = ParameterType
    context_object_name = "parameter"
    kit: MeasurementKit

    def get_queryset(self):
        self.kit = get_object_or_404(MeasurementKit, pk=self.kwargs.get("pk_kit"))
        return super(ODConverterDetailView, self).get_queryset()

    def get_context_data(self, **kwargs):
        kwargs["calibrations"] = (
            Calibration.objects.filter(
                parameter_type=self.object,
                measurement_kit=self.kit,
            )
            .order_by("pk")
            .all()
        )
        kwargs["kit"] = self.kit
        return super(ODConverterDetailView, self).get_context_data(**kwargs)
