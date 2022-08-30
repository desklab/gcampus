#  Copyright (C) 2021-2022 desklab gUG (haftungsbeschränkt)
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

import httpx
from django.contrib.gis import admin
from django.db import transaction
from django.db.models import QuerySet
from django.utils.html import escape, format_html
from django.utils.translation import gettext_lazy as _
from leaflet.admin import LeafletGeoAdmin

from gcampus.core.models import (
    Measurement,
    ParameterType,
    Parameter,
    Limit,
    Water,
    Calibration,
)
from gcampus.core.models.util import ADMIN_READ_ONLY_FIELDS


def hide(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):  # noqa
    queryset.update(hidden=True)


def osm_update(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):  # noqa
    with transaction.atomic():
        with httpx.Client as client:
            water: Water  # Used for type hints
            for water in queryset:
                water.update_from_osm(client=client)
                water.save()


def show(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):  # noqa
    queryset.update(hidden=False)


hide.short_description = _("Hide selected items for all users")
show.short_description = _("Show selected items for all users")
osm_update.short_description = _("Update from OpenStreetMap")


class MeasurementInline(admin.TabularInline):
    show_change_link = True
    model = Measurement
    fields = ("name", "water")
    extra = 0


class ParameterInline(admin.TabularInline):
    show_change_link = True
    model = Parameter
    extra = 0


class MeasurementAdmin(LeafletGeoAdmin):
    search_fields = (
        "name",
        "water__name",
        "location_name",
        "comment",
    )
    list_filter = ("hidden", "requires_review", "time", "updated_at")
    list_display = (
        "__str__",
        "name",
        "water_name",
        "location_name",
        "time",
        "token",
        "hidden",
        "requires_review",
    )
    list_display_links = ("__str__",)
    inlines = [ParameterInline]
    readonly_fields = ADMIN_READ_ONLY_FIELDS + ("location_name",)
    actions = [hide, show]

    def get_queryset(self, request):
        """
        Return a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        qs = Measurement.all_objects.all()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


class WaterAdmin(LeafletGeoAdmin):
    search_fields = ("name", "osm_id")
    list_filter = ("osm_element_type", "flow_type", "requires_update")
    list_display = (
        "display_name",
        "osm_id",
        "flow_type",
        "water_type",
        "updated_at",
        "requires_update",
    )
    inlines = [MeasurementInline]
    actions = (osm_update,)
    readonly_fields = ADMIN_READ_ONLY_FIELDS + ("osm_url",)

    @admin.display(description=_("OpenStreetMap URL"))
    def osm_url(self, instance: Water):
        if not instance.osm_id:
            return format_html(
                "<span class='errors'>{error_message}</span>",
                error_message=_("No OpenStreetMap ID provided!"),
            )
        url: str = escape(instance.osm_url)
        return format_html('<a href="{url}">{url}</a>', url=url)


class ParameterTypeAdmin(admin.ModelAdmin):
    inlines = [ParameterInline]


class LimitAdmin(admin.ModelAdmin):
    pass


class CalibrationAdmin(admin.ModelAdmin):
    pass


class ParameterAdmin(admin.ModelAdmin):
    search_fields = ("parameter_type__name",)
    list_filter = ("parameter_type", "hidden")
    list_display = (
        "__str__",
        "parameter_type",
        "measurement",
        "hidden",
    )
    readonly_fields = ADMIN_READ_ONLY_FIELDS
    default_manager_name = "all_objects"
    actions = [hide, show]


admin.site.register(Measurement, MeasurementAdmin)
admin.site.register(ParameterType, ParameterTypeAdmin)
admin.site.register(Parameter, ParameterAdmin)
admin.site.register(Limit, LimitAdmin)
admin.site.register(Water, WaterAdmin)
admin.site.register(Calibration, CalibrationAdmin)
