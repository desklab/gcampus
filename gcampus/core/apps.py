from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GCampusCoreAppConfig(AppConfig):
    name = "gcampus.core"
    label = "gcampuscore"
    verbose_name = _("GCampus Core")
