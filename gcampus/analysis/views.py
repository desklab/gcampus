from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

from gcampus.core.models import ParameterType
from gcampus.core.views.base import TitleMixin


class ODConverterView(TitleMixin, ListView):
    title = _("Optical Density Converter")
    template_name = "gcampusanalysis/od_converter.html"
    model = ParameterType
