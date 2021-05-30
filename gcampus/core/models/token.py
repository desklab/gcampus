from django.contrib.gis.db import models

from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _

from django.conf import settings

ALLOWED_TOKEN_CHARS = settings.ALLOWED_TOKEN_CHARS


class TeacherToken(models.Model):
    token = models.CharField(blank=False, max_length=12, unique=True)

    deactivated = models.BooleanField(default=False)

    school_name = models.CharField(
        blank=True, max_length=140, verbose_name=_("School Name")
    )

    teacher_name = models.CharField(
        blank=True, max_length=140, verbose_name=_("Teacher Name")
    )

    class Meta:
        verbose_name = _("Teacher Token")

    def generate_teacher_token(self):
        token_set = False
        while not token_set:
            token = get_random_string(length=12, allowed_chars=ALLOWED_TOKEN_CHARS)
            if not TeacherToken.objects.filter(token=token).exist():
                return token

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_teacher_token()
        return super().save(*args, **kwargs)

    def __str__(self):
        return str(self.pk)


class StudentToken(models.Model):
    token = models.CharField(blank=False, max_length=8, unique=True)

    parent_token = models.ForeignKey(
        TeacherToken, on_delete=models.PROTECT, blank=False, null=False
    )

    deactivated = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Student Token")

    def generate_student_token(self):
        token_set = False
        while not token_set:
            token = get_random_string(length=8, allowed_chars=ALLOWED_TOKEN_CHARS)
            if not StudentToken.objects.filter(token=token).exist():
                return token

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_student_token()
        return super().save(*args, **kwargs)

    def __str__(self):
        return str(self.pk)
