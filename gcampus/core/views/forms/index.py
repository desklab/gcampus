#  Copyright (C) 2022 desklab gUG (haftungsbeschränkt)
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
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView

from gcampus.core.decorators import require_permission_edit_measurement
from gcampus.core.forms.measurement import StructureIndexForm
from gcampus.core.models import StructureIndex, Measurement
from gcampus.core.models.water import FlowType
from gcampus.core.views.forms.tabs import MeasurementEditTabsMixin


class StructureIndexEditView(MeasurementEditTabsMixin, UpdateView):
    model = StructureIndex
    form_class = StructureIndexForm
    current_tab_name = "structure"
    template_name = "gcampuscore/forms/structure-index.html"
    next_view_name = "gcampuscore:measurement-detail"

    @method_decorator(require_permission_edit_measurement)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_object(self, queryset=None) -> model:
        measurement: Measurement = get_object_or_404(
            Measurement, pk=self.kwargs.get(self.pk_url_kwarg)
        )
        if measurement.water.flow_type != FlowType.RUNNING:
            raise Http404("Index not supported")
        return get_object_or_404(self.model, measurement=measurement)
