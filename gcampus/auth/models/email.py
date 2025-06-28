from django.db import models
from django.utils.translation import gettext_lazy as _

from gcampus.core.models.util import DateModelMixin


class BlockedEmail(DateModelMixin):
    class Meta:
        verbose_name = _("Blocked email")
        verbose_name_plural = _("Blocked emails")

    email = models.EmailField(blank=False, max_length=254, verbose_name=_("email"))
    #: Internal comment used in the review process. Should not be
    #: public.
    internal_comment = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("internal comment"),
    )


def check_email(email: str) -> bool:
    try:
        _, domain = email.split("@")
        wildcard = f"*@{domain}"
        query = models.Q(email=email) | models.Q(email=wildcard)
    except ValueError:
        query = models.Q(email=email)
    return not BlockedEmail.objects.filter(query).exists()
