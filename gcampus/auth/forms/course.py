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
    "GenerateAccessKeysForm",
    "CourseForm",
    "RegisterForm",
    "AccessKeyDeactivationForm",
]

import logging

from django import forms
from django.conf import settings
from django.contrib import messages
from django.core import validators
from django.db import transaction
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy, get_language

from gcampus.auth.models import Course, AccessKey, CourseToken
from gcampus.auth.models.course import (
    default_token_generator,
    EmailConfirmationTokenGenerator,
)
from gcampus.auth.tasks import send_email_confirmation_email

logger = logging.getLogger("gcampus.auth.forms.course")


def create_email_change_url(
    course: Course, token_generator: EmailConfirmationTokenGenerator
) -> str:
    """Create email change confirmation URL. When vising this URL, the
    email will be confirmed.

    :param course: The course associated with the email change or
        initial confirmation.
    :param token_generator: A token generator used to create the token.
    """
    return reverse(
        "gcampusauth:email-confirmation",
        kwargs={
            "courseidb64": urlsafe_base64_encode(force_bytes(course.pk)),
            "token": token_generator.make_token(course),
        },
    )


def send_confirmation_email(
    email: str, course: Course, token_generator: EmailConfirmationTokenGenerator
):
    """Send confirmation email (asynchronously). If ``DEBUG`` is
    enabled, the confirmation link will be logged using the default
    logger.

    :param email: Email address to which the confirmation shall be sent.
    :param course: The course object used to construct the signed
        confirmation token.
    :param token_generator: Token generator. Use the
        :attr:`gcampus.auth.models.course.default_token_generator` if
        unsure.
    """
    url = create_email_change_url(course, token_generator)
    if settings.DEBUG:
        logger.info(f"Email confirmation link: {url}")
    send_email_confirmation_email.apply_async(
        args=(email, url), kwargs=dict(language=get_language())
    )


class GenerateAccessKeysForm(forms.ModelForm):
    """This form is used to generate new access keys for a given course.
    Note that the amount of access keys that can be associated with a
    course is limited by ``REGISTER_MAX_ACCESS_KEY_NUMBER`` in the
    project settings.
    """

    instance: Course
    count = forms.IntegerField(
        label=gettext_lazy("Count"),
        min_value=1,
        initial=1,
        # the max value validator is added dynamically in the
        # ``_clean_fields`` method.
    )

    class Meta:
        model = Course
        fields = tuple()  # do not use any field here

    def __init__(self, *args, **kwargs):
        super(GenerateAccessKeysForm, self).__init__(*args, **kwargs)
        if self.instance is None:
            # Make sure the instance is set
            raise ValueError("Unable to validate form if no instance is provided")

        max_count = getattr(settings, "REGISTER_MAX_ACCESS_KEY_NUMBER", 30)
        current_count = self.instance.access_keys.count()
        allowed_count = max_count - current_count
        # Append the max value validator depending on the number of
        # allowed access keys.
        self.fields["count"].max_value = allowed_count
        self.fields["count"].validators.append(
            validators.MaxValueValidator(allowed_count)
        )

    def save(self, commit=True):
        if not commit:
            # For now, 'commit=False' is not needed. The code below
            # does not support creating access keys without saving them
            # right away.
            raise NotImplementedError(
                "Calling 'save' with 'commit=False' is not supported."
            )
        with transaction.atomic():
            for _ in range(self.cleaned_data["count"]):
                AccessKey.objects.create_token(self.instance)
            super(GenerateAccessKeysForm, self).save(commit=commit)
        return self.instance


class CourseForm(forms.ModelForm):
    """The course edit form is used to modify the course data such as
    its name and the email address associated with the course.
    When changing the email address, a confirmation email will be sent
    to the new address.
    """

    email = forms.EmailField(max_length=254, required=True, label=gettext_lazy("email"))

    class Meta:
        model = Course
        fields = ("name", "school_name", "teacher_name", "email")

    def __init__(self, instance: Course, *, initial=None, **kwargs):
        if initial is None:
            initial = {}
        initial.setdefault("email", instance.teacher_email)
        kwargs["instance"] = instance
        kwargs["initial"] = initial
        super(CourseForm, self).__init__(**kwargs)

    def save(self, request=None, token_generator=default_token_generator, commit=True):
        initial_email = self.initial.get("email", self.instance.teacher_email)
        new_email = self.cleaned_data["email"]
        if self.fields["email"].has_changed(initial_email, new_email):
            # The email has been modified. Set the field ``new_email``
            # to the changed email and send a confirmation email.
            self.instance.new_email = new_email
            self.send_email(new_email, token_generator)
            if request is not None:
                messages.success(
                    request,
                    message=gettext_lazy(
                        "An email has been sent to '{new_email!s}'. "
                        "Please confirm your new email address "
                        "by clicking the link in the email. "
                        "It may take a few minutes for the email to arrive."
                    ).format(new_email=new_email),
                )
        return super(CourseForm, self).save(commit=commit)

    def send_email(self, email: str, token_generator: EmailConfirmationTokenGenerator):
        send_confirmation_email(email, self.instance, token_generator)


class RegisterForm(forms.ModelForm):
    """The register form creates a new course with
    :attr:`number_of_access_keys` new access keys. Note that the course
    will be disabled by default as the email will not be confirmed.
    Thus, the user also receives a confirmation email.
    """

    number_of_access_keys = forms.IntegerField(
        min_value=1,
        max_value=getattr(settings, "REGISTER_MAX_ACCESS_KEY_NUMBER", 30),
        required=True,
        initial=5,
        label=gettext_lazy("Number of access keys"),
    )

    class Meta:
        model = Course
        fields = (
            "school_name",
            "teacher_name",
            "teacher_email",
            "name",
        )

    def save(self, token_generator=default_token_generator, commit=True):
        with transaction.atomic():
            obj: Course = super(RegisterForm, self).save(commit=commit)
            # Create the main course token
            CourseToken.objects.create_token(obj)
            for _ in range(self.cleaned_data["number_of_access_keys"]):
                # Create the desired number of access keys. The
                # 'token' field is generated automatically.
                AccessKey.objects.create_token(obj)

        # Send the registration email
        self.send_email(obj.teacher_email, token_generator)
        return obj

    def send_email(self, email: str, token_generator: EmailConfirmationTokenGenerator):
        send_confirmation_email(email, self.instance, token_generator)


class AccessKeyDeactivationForm(forms.ModelForm):
    """This form is only used to activate or deactivate access keys in
    the course administration.
    """

    class Meta:
        model = AccessKey
        fields = ("deactivated",)
