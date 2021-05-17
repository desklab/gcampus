from django.contrib.gis.db import models

from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _

class TeacherToken(models.Model):
    token = models.CharField(blank=False, max_length=16)

    class Meta:
        verbose_name = _("Teacher Token")

    def generate_teacher_token(self):
        return get_random_string(length=16)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_teacher_token()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.token


class StudentToken(models.Model):
    token = models.CharField(blank=False, max_length=16)

    parent_token = models.ForeignKey(TeacherToken, on_delete=models.PROTECT, blank=False, max_length=16)

    class Meta:
        verbose_name = _("Student Token")

    def generate_student_token(self, teacher_token):
        if TeacherToken.objects.filter(teacher_token) is not None:
            return get_random_string(length=16)
        else:
            return None

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_student_token()
        return super().save(*args, **kwargs)
