from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GCampusToolsAppConfig(AppConfig):
    name = "gcampus.tools"
    label = "gcampustools"
    verbose_name = _("GCampus Tools")
