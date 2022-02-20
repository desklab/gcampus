from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GcampusMailConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "gcampus.mail"
    label = "gcampusmail"
    verbose_name = _("GCampus E-Mail")
