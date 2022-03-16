#  Copyright (C) 2021 desklab gUG (haftungsbeschränkt)
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

from django.contrib.gis import admin
from django.db.models import QuerySet
from django.utils.html import format_html_join, escape, format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from leaflet.admin import LeafletGeoAdmin

from gcampus.core.models import Measurement, ParameterType, Parameter, Limit, Water
from gcampus.core.models.util import ADMIN_READ_ONLY_FIELDS


def hide(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):  # noqa
    queryset.update(hidden=True)


def show(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):  # noqa
    queryset.update(hidden=False)


hide.short_description = _("Hide selected items for all users")
show.short_description = _("Show selected items for all users")


class MeasurementAdmin(LeafletGeoAdmin):
    list_filter = ("hidden",)
    readonly_fields = ADMIN_READ_ONLY_FIELDS + ("location_name",)
    actions = [hide, show]


class WaterAdmin(LeafletGeoAdmin):
    list_display = (
        "display_name", "osm_id", "flow_type", "water_type", "updated_at"
    )
    readonly_fields = ADMIN_READ_ONLY_FIELDS + ("osm_url",)

    @admin.display(description=_('OpenStreetMaps URL'))
    def osm_url(self, instance: Water):
        if not instance.osm_id:
            return format_html(
                "<span class='errors'>{error_message}</span>",
                error_message=_("No OpenStreetMaps ID provided!")
            )
        url: str = escape(
            "https://www.openstreetmap.org/"
            f"{instance.osm_element_type}/{instance.osm_id}"
        )
        return format_html('<a href="{url}">{url}</a>', url=url)


class ParameterTypeAdmin(admin.ModelAdmin):
    pass


class LimitAdmin(admin.ModelAdmin):
    pass


class ParameterAdmin(admin.ModelAdmin):
    readonly_fields = ADMIN_READ_ONLY_FIELDS
    list_filter = ("hidden",)
    default_manager_name = "all_objects"
    actions = [hide, show]


admin.site.register(Measurement, MeasurementAdmin)
admin.site.register(ParameterType, ParameterTypeAdmin)
admin.site.register(Parameter, ParameterAdmin)
admin.site.register(Limit, LimitAdmin)
admin.site.register(Water, WaterAdmin)
