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

__all__ = [
    "update_measurement_document",
    "clear_measurement_documents",
    "update_measurement_indices",
    "create_measurement_indices",
]

import logging
from typing import Union, Optional

from django.db import transaction
from django.db.models import QuerySet
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.translation import get_language

from gcampus.core.models import (
    Parameter,
    Measurement,
    ParameterType,
    Water,
    BACHIndex,
    SaprobicIndex,
    TrophicIndex,
    StructureIndex,
)
from gcampus.documents.tasks import render_cached_document_view

logger = logging.getLogger("gcampus.core.receivers")


@receiver(post_save, sender=Measurement)
@receiver(post_save, sender=Parameter)
@receiver(post_delete, sender=Parameter)
def update_measurement_document(
    sender,  # noqa
    instance: Union[Parameter, Measurement],
    created: bool = False,
    update_fields: Optional[Union[tuple, list]] = None,
    **kwargs,  # noqa
):
    update_fields = update_fields or ()

    if isinstance(instance, Measurement):
        if "document" in update_fields:
            return
        if created:
            return
        measurement: Measurement = instance
    elif isinstance(instance, Parameter):
        measurement: Measurement = instance.measurement
    else:
        raise NotImplementedError(f"Unhandled instance '{type(instance)}'")

    if measurement.hidden:
        # Do not build documents for hidden measurements. Make sure to
        # delete old documents.
        if measurement.document:
            measurement.document.delete(save=True)
        return

    if not measurement.document:
        # Only build the document if it has been build already.
        return

    render_cached_document_view.apply_async(
        args=(
            "gcampus.documents.views.MeasurementDetailPDF",
            measurement.pk,
            get_language(),
        ),
    )


@receiver(post_save, sender=ParameterType)
def clear_measurement_documents(
    sender,  # noqa
    instance: ParameterType,
    created: bool = False,
    **kwargs,  # noqa
):
    if created:
        return
    qs: QuerySet
    if isinstance(instance, ParameterType):
        qs = Measurement.objects.filter(parameters__parameter_type=instance)
    elif isinstance(instance, Water):
        qs = Measurement.objects.filter(water=instance)
    else:
        raise NotImplementedError(f"Unhandled instance '{type(instance)}'")
    # Note that the file will not be deleted from the storage backend,
    # only its reference is removed from the database.
    qs.update(document=None)


@receiver(post_save, sender=Parameter)
def update_measurement_indices(sender, instance: Parameter, **kwargs):
    with transaction.atomic:
        instance.measurement.bach_index.update()
        instance.measurement.saprobic_index.update()
        instance.measurement.trophic_index.update()
        instance.measurement.structure_index.update()


@receiver(post_save, sender=Measurement)
def create_measurement_indices(
    sender, instance: Measurement, created: bool = False, **kwargs
):
    if created:
        BACHIndex.objects.get_or_create(measurement_id=instance.pk)
        SaprobicIndex.objects.get_or_create(measurement_id=instance.pk)
        TrophicIndex.objects.get_or_create(measurement_id=instance.pk)
        StructureIndex.objects.get_or_create(measurement_id=instance.pk)
