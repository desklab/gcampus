from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GCampusAuthAppConfig(AppConfig):
    name = "gcampus.auth"
    label = "gcampusauth"
    verbose_name = _("GCampus Auth")
