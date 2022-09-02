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

from django.contrib.gis import admin
from django.db import transaction
from django.db.models import QuerySet
from django.utils.html import escape, format_html
from django.utils.translation import gettext_lazy as _
from leaflet.admin import LeafletGeoAdmin

from gcampus.admin.options import LinkedInlineMixin
from gcampus.core.models import (
    Measurement,
    ParameterType,
    Parameter,
    Water,
    Calibration,
    BACHIndex,
    SaprobicIndex,
    TrophicIndex,
    StructureIndex,
)
from gcampus.core.models.util import ADMIN_READ_ONLY_FIELDS


def hide(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):  # noqa
    queryset.update(hidden=True)


def osm_update(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):  # noqa
    water: Water
    with transaction.atomic():
        for water in queryset:
            water.update_from_osm()
            water.save()


def show(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):  # noqa
    queryset.update(hidden=False)


hide.short_description = _("Hide selected items for all users")
show.short_description = _("Show selected items for all users")
osm_update.short_description = _("Update from OpenStreetMap")


class MeasurementInline(LinkedInlineMixin, admin.TabularInline):
    model = Measurement
    fields = ("name", "water") + LinkedInlineMixin.readonly_fields
    extra = 0


class ParameterInline(LinkedInlineMixin, admin.TabularInline):
    model = Parameter
    extra = 0


@admin.action(description=_("Create or update Water Quality Indices"))
def create_or_update_indices(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):
    measurement: Measurement
    with transaction.atomic():
        for measurement in queryset:
            bach_index, created = BACHIndex.objects.get_or_create(
                measurement_id=measurement.pk
            )
            bach_index.update()

            saprobic_index, created = SaprobicIndex.objects.get_or_create(
                measurement_id=measurement.pk
            )
            saprobic_index.update()

            structure_index, created = StructureIndex.objects.get_or_create(
                measurement_id=measurement.pk
            )
            structure_index.update()

            trophic_index, created = TrophicIndex.objects.get_or_create(
                measurement_id=measurement.pk
            )
            trophic_index.update()


class MeasurementAdmin(LeafletGeoAdmin):
    list_filter = ("hidden",)
    inlines = [ParameterInline]
    readonly_fields = ADMIN_READ_ONLY_FIELDS + ("location_name",)
    actions = [hide, show, create_or_update_indices]

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
    list_display = ("display_name", "osm_id", "flow_type", "water_type", "updated_at")
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
        url: str = escape(
            "https://www.openstreetmap.org/"
            f"{instance.osm_element_type}/{instance.osm_id}"
        )
        return format_html('<a href="{url}">{url}</a>', url=url)


class ParameterTypeAdmin(admin.ModelAdmin):
    inlines = [ParameterInline]


class CalibrationAdmin(admin.ModelAdmin):
    pass


class ParameterAdmin(admin.ModelAdmin):
    readonly_fields = ADMIN_READ_ONLY_FIELDS
    list_filter = ("hidden",)
    default_manager_name = "all_objects"
    actions = [hide, show]


@admin.action(description=_("Recalculate selected indices"))
def update_bach_index(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):
    index: BACHIndex
    with transaction.atomic():
        for index in queryset:
            index.update()


class BACHIndexAdmin(admin.ModelAdmin):
    actions = [update_bach_index]


@admin.action(description=_("Recalculate selected indices"))
def update_saprobic_index(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):
    index: SaprobicIndex
    with transaction.atomic():
        for index in queryset:
            index.update()


class SaprobicIndexAdmin(admin.ModelAdmin):
    actions = [update_saprobic_index]


@admin.action(description=_("Recalculate selected indices"))
def update_trophic_index(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):
    index: TrophicIndex
    with transaction.atomic():
        for index in queryset:
            index.update()


class TrophicIndexAdmin(admin.ModelAdmin):
    actions = [update_trophic_index]


@admin.action(description=_("Recalculate selected indices"))
def update_structure_index(modeladmin: admin.ModelAdmin, request, queryset: QuerySet):
    index: StructureIndex
    with transaction.atomic():
        for index in queryset:
            index.update()


class StructureIndexAdmin(admin.ModelAdmin):
    actions = [update_structure_index]


admin.site.register(Measurement, MeasurementAdmin)
admin.site.register(ParameterType, ParameterTypeAdmin)
admin.site.register(Parameter, ParameterAdmin)
admin.site.register(Water, WaterAdmin)
admin.site.register(Calibration, CalibrationAdmin)
admin.site.register(BACHIndex, BACHIndexAdmin)
admin.site.register(SaprobicIndex, SaprobicIndexAdmin)
admin.site.register(TrophicIndex, TrophicIndexAdmin)
admin.site.register(StructureIndex, StructureIndexAdmin)
