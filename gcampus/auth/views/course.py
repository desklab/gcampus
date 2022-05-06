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

__all__ = [
    "CourseUpdateView",
    "EmailConfirmationView",
    "AccessKeyCreateView",
    "AccessKeyDeactivationView",
]

import logging
from datetime import datetime
from typing import Optional, List

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect, HttpRequest, Http404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext, get_language
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic.edit import UpdateView, ProcessFormView, FormMixin
from django.views.generic.list import (
    MultipleObjectMixin,
    MultipleObjectTemplateResponseMixin,
)

from gcampus.auth import session
from gcampus.auth.decorators import require_course_token, require_permissions, throttle
from gcampus.auth.exceptions import TokenPermissionError
from gcampus.auth.forms import (
    CourseForm,
    GenerateAccessKeysForm,
    AccessKeyDeactivationForm,
)
from gcampus.auth.models import Course
from gcampus.auth.models.course import (
    default_token_generator,
    EmailConfirmationTokenGenerator,
)
from gcampus.auth.models.token import AccessKey, CourseToken, TokenType
from gcampus.auth.tasks import send_registration_email
from gcampus.core.views.base import TitleMixin
from gcampus.core import settings

logger = logging.getLogger("gcampus.auth.views.course")


class CourseUpdateView(TitleMixin, UpdateView):
    form_class = CourseForm
    model = Course
    object: Course
    template_name_suffix = "_edit_form"
    success_url = reverse_lazy("gcampusauth:course-update")
    title = _("Course data")

    @method_decorator(require_course_token)
    def dispatch(self, request, *args, **kwargs):
        return super(CourseUpdateView, self).dispatch(request, *args, **kwargs)

    @method_decorator(require_permissions("gcampusauth.change_course"))
    @method_decorator(throttle())  # Throttled to avoid email spam
    def post(self, request, *args, **kwargs):
        return super(CourseUpdateView, self).post(request, *args, **kwargs)

    def form_valid(self, form: CourseForm):
        """If the form is valid, save the associated model."""
        self.object = form.save(request=self.request)
        return HttpResponseRedirect(self.get_success_url())

    def get_object(self, queryset=None):
        token: CourseToken = self.request.token
        if not isinstance(token, CourseToken):
            raise RuntimeError("At this point 'request.toke' has to be a course token!")
        return token.course

    def get_context_data(self, **kwargs):
        return super(CourseUpdateView, self).get_context_data(**kwargs)


class AccessKeyCreateView(
    TitleMixin,
    MultipleObjectTemplateResponseMixin,
    MultipleObjectMixin,
    FormMixin,
    ProcessFormView,
):
    form_class = GenerateAccessKeysForm
    model = AccessKey
    object_list: List[AccessKey]
    success_url = reverse_lazy("gcampusauth:course-access-keys")
    title = _("Access keys")

    @method_decorator(require_course_token)
    def dispatch(self, request, *args, **kwargs):
        self.object_list = self.get_queryset().prefetch_related("measurements")
        return super(AccessKeyCreateView, self).dispatch(request, *args, **kwargs)

    @method_decorator(require_permissions("gcampusauth.add_accesskey"))
    def post(self, request, *args, **kwargs):
        return super(AccessKeyCreateView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            gettext("You successfully generated {count:d} new access keys").format(
                count=form.cleaned_data["count"]
            ),
        )
        return super(AccessKeyCreateView, self).form_valid(form)

    def get_course(self) -> Course:
        token: CourseToken = self.request.token
        if not isinstance(token, CourseToken):
            raise RuntimeError(
                "At this point 'request.token' has to be a course token!"
            )
        return token.course

    def get_form_kwargs(self):
        kwargs = super(AccessKeyCreateView, self).get_form_kwargs()
        kwargs.update({"instance": self.get_course()})
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs.setdefault("today", datetime.now())
        kwargs["access_keys_max_count"] = getattr(
            settings, "REGISTER_MAX_ACCESS_KEY_NUMBER", 30
        )
        return super(AccessKeyCreateView, self).get_context_data(**kwargs)

    def get_queryset(self):
        return self.get_course().access_keys.all()


class EmailConfirmationView(View):
    redirect_url = reverse_lazy("gcampusauth:course-update")
    token_generator: EmailConfirmationTokenGenerator = default_token_generator

    @method_decorator(throttle())  # Try to avoid brute force
    def get(self, request: HttpRequest, courseidb64: str, token: str, *args, **kwargs):
        course: Optional[Course]
        try:
            course_pk = urlsafe_base64_decode(courseidb64).decode()
            course = Course.objects.prefetch_related("course_token").get(pk=course_pk)
        except (TypeError, ValueError, OverflowError, Course.DoesNotExist):
            course = None
        if course is not None and self.token_generator.check_token(course, token):
            if not course.email_verified:
                course_registered = True
                # The course has only recently been registered and the
                # user just confirmed their email. Thus, the course will
                # now become active.
                course.email_verified = True
                # Note that in this case, the field ``teacher_email``
                # contains the email that has just been verified whereas
                # ``new_email`` is set to ``None``.
                message = _("All done! The course you registered is now active.")
            else:
                course_registered = False
                # The course is already active and this has been
                # triggered by an email change using the course edit
                # form in the course administration.
                course.teacher_email = course.new_email
                course.new_email = None
                message = _(
                    "Email confirmed. You email is now set to {new_email!s}."
                ).format(new_email=course.teacher_email)
            with transaction.atomic():
                # Use an atomic transaction as ``session.set_token``
                # will alter the course token object (set last login
                # time)
                course.save()
                course_token = course.course_token
                if (
                    session.is_authenticated(request)
                    and request.token.pk is not course_token.pk
                ):
                    # The user is currently logged in with a course
                    # token or access key that does not match the
                    # provided course. Thus, the user is logged out and
                    # informed of that using a message.
                    messages.warning(
                        request,
                        message=_(
                            "It seems like you have been logged in with a different "
                            "course token or with an access key. You have been logged "
                            "out and are now logged in with the course token of your "
                            "email address."
                        ),
                    )
                session.set_token(request, course_token, TokenType.course_token)
            if course_registered:
                # Send the registration email
                send_registration_email.apply_async(
                    args=(course.pk,), kwargs=dict(language=get_language())
                )
            messages.success(request, message=message)
            return HttpResponseRedirect(self.redirect_url)
        else:
            raise Http404()


class AccessKeyDeactivationView(UpdateView):
    model = AccessKey
    form_class = AccessKeyDeactivationForm
    success_url = reverse_lazy("gcampusauth:course-access-keys")

    @method_decorator(require_POST)
    @method_decorator(require_course_token)
    @method_decorator(require_permissions("gcampusauth.change_accesskey"))
    def dispatch(self, request, pk, *args, **kwargs):
        return super(AccessKeyDeactivationView, self).dispatch(
            request, pk, *args, **kwargs
        )

    def _get_course_token(self) -> CourseToken:
        token: CourseToken = self.request.token
        if not isinstance(token, CourseToken):
            raise RuntimeError(
                "The 'dispatch' method should be decorated to only allow a "
                "'CourseToken' to access this view."
            )
        return token

    def form_valid(self, form):
        token: CourseToken = self._get_course_token()
        if not token.has_perm("gcampusauth.change_accesskey", obj=self.object):
            raise TokenPermissionError()
        return super(AccessKeyDeactivationView, self).form_valid(form)

    def get_queryset(self):
        queryset = super(AccessKeyDeactivationView, self).get_queryset()
        # Limiting the queryset to the current course will automatically
        # raise a ``Http404`` exception if the user tries to modify an
        # access key that they do not have the permission to edit.
        return queryset.filter(course_id=self._get_course_token().course_id).all()
