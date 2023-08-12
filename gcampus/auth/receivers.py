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

import logging
from typing import Optional, Union, Type

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import get_language

from gcampus.auth.models import Course, AccessKey, BaseToken
from gcampus.auth.signals import token_user_logged_in
from gcampus.documents.tasks import render_cached_document_view

logger = logging.getLogger("gcampus.auth.recievers")


@receiver(post_save, sender=Course)
def update_course(
    sender,  # noqa
    instance: Course,
    created: bool = False,
    update_fields: Optional[Union[tuple, list]] = None,
    **kwargs,  # noqa
):
    """Post-save signal receiver for course token

    This function will update all documents that may require a rebuild
    when as the model has changed.
    """
    update_fields = update_fields or ()
    if "overview_document" in update_fields and not created:
        # The overview document has been changed on purpose
        return
    if not instance.email_verified:
        logger.debug(
            "The course is still inactive. No need to spend resources on creating the "
            "document for this course."
        )
        return
    render_cached_document_view.apply_async(
        args=(
            "gcampus.documents.views.CourseOverviewPDF",
            instance.pk,
            get_language(),
        ),
    )


@receiver(token_user_logged_in)
def update_last_token_login(sender, instance: BaseToken, **kwargs):  # noqa
    instance.last_login = timezone.now()
    instance.save(update_fields=["last_login"])


@receiver(post_save, sender=AccessKey)
@receiver(post_delete, sender=AccessKey)
def update_access_key_documents(
    sender: Type[AccessKey],
    instance: AccessKey,
    *args,
    update_fields: Optional[Union[tuple, list]] = None,
    **kwargs,  # noqa
):
    """Post-save and -delete signal receiver for access keys

    Access keys are typically displayed in various documents of a
    given course.
    A rebuild is required every time an access key changes or is
    deleted. These changes may include e.g. disabling access keys or
    changes made in the admin interface.

    :param sender: The sender. This is always the type
        :class:`AccessKey`
    :param instance: The modified instance. Used to retrieve the
        associated course.
    :param args: Additional arguments passed by the signal
    :param update_fields: Optional list of updated fields
    :param kwargs: Additional keyword arguments passed by the signal
    """
    if kwargs.get("created", False):
        logger.debug("Access key has been created, skip updating 'CourseOverviewPDF'.")
        return
    if update_fields and len(update_fields) == 1 and "last_login" in update_fields:
        # Triggered by updating the 'last_login' field, e.g. from the
        # 'update_last_token_login' function.
        logger.debug("User logged in, skip updating 'CourseOverviewPDF'.")
        return
    course: Course = instance.course
    render_cached_document_view.apply_async(
        args=(
            "gcampus.documents.views.CourseOverviewPDF",
            course.pk,
            get_language(),
        ),
    )
