from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GCampusAnalysisAppConfig(AppConfig):
    name = "gcampus.analysis"
    label = "gcampusanalysis"
    verbose_name = _("GCampus Core")
