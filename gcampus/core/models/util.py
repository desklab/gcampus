from django.db import models

ADMIN_READ_ONLY_FIELDS = ("created_at", "updated_at")

EMPTY = ("", None, False, (), [], {})


class DateModelMixin(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

