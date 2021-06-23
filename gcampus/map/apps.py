from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GCampusMapAppConfig(AppConfig):
    name = "gcampus.map"
    label = "gcampusmap"
    verbose_name = _("GCampus Map")
