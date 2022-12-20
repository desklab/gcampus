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

__all__ = ["MEASUREMENT_FORM_TABS", "MeasurementEditTabsMixin"]

from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from gcampus.core.models import Measurement
from gcampus.core.models.index.base import WaterQualityIndex
from gcampus.core.models.water import FlowType
from gcampus.core.tabs import TabNavigation, Tab
from gcampus.core.views.base import TabsMixin, TitleMixin

MEASUREMENT_FORM_TABS = TabNavigation(
    meta=Tab(
        _("1. Metadata"),
        view_name="gcampuscore:edit-measurement",
        vn_requires_args=True,
    ),
    chemical=Tab(
        _("2. Measured Parameters"),
        view_name="gcampuscore:edit-chemical-parameters",
        vn_requires_args=True,
    ),
    biological=Tab(
        _("3. Saprobic Abundances"),
        view_name="gcampuscore:edit-biological-parameters",
        vn_requires_args=True,
    ),
    structure=Tab(
        _("4. Structural Assessment"),
        view_name="gcampuscore:edit-structure-index",
        vn_requires_args=True,
    ),
)


class MeasurementEditTabsMixin(TitleMixin, TabsMixin):
    request: HttpRequest
    object: Measurement
    instance: Measurement
    next_view_name: str
    tabs = MEASUREMENT_FORM_TABS

    def get_title(self) -> str:
        return gettext("Edit {measurement!s}").format(
            measurement=self._get_measurement()
        )

    def get_success_url(self) -> str:
        return reverse(self.next_view_name, kwargs={"pk": self._get_measurement().pk})

    def _get_measurement(self) -> Measurement:
        """Get current measurement from ``self``. As this mixin may be
        used by different view classes that do not all provide a common
        interface to the measurement instance, this method checks for
        the presence of the ``object`` and ``instance`` attribute.
        If the instance is of type
        :class:`gcampus.core.models.index.base.WaterQualityIndex`, the
        related measurement is returned.
        """
        if hasattr(self, "object"):
            if isinstance(self.object, WaterQualityIndex):
                return self.object.measurement
            return self.object
        elif hasattr(self, "instance"):
            return self.instance
        else:
            raise RuntimeError("Neither 'object' nor 'instance' are available.")

    def _get_flow_type(self) -> FlowType:
        """Retrieve the flow type of the current measurement."""
        return self._get_measurement().water.flow_type

    def get_tabs(self) -> TabNavigation:
        # Create a deep copy of the tabs to avoid mutation and
        # side effects
        tabs: TabNavigation = super(MeasurementEditTabsMixin, self).get_tabs()
        # Set chemical and meta urls
        reverse_kwargs = {"pk": self._get_measurement().pk}
        tabs["meta"].set_url_from_view_name(reverse_kwargs=reverse_kwargs)
        tabs["chemical"].set_url_from_view_name(reverse_kwargs=reverse_kwargs)
        # The tabs 'biological' and 'structure' are only supported by
        # waters of flow type 'running'. If the water is not of that
        # type, the tabs are instead being disabled.
        only_running_keys = ["biological", "structure"]
        for key in only_running_keys:
            if self._get_flow_type() == FlowType.RUNNING:
                tabs[key].set_url_from_view_name(reverse_kwargs=reverse_kwargs)
            else:
                tabs[key].disabled = True
        return tabs
