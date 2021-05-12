from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GCampusAPIAppConfig(AppConfig):
    name = "gcampus.api"
    label = "gcampusapi"
    verbose_name = _("GCampus API")
