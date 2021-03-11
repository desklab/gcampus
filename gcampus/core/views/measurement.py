from django.views.generic import ListView
from django.views.generic.edit import FormView

from gcampus.core.forms.measurement import MeasurementForm
from gcampus.core.models import Measurement


class MeasurementListView(ListView):
    model = Measurement


class MeasurementFormView(FormView):
    template_name = "gcampuscore/forms/measurement.html"
    form_class = MeasurementForm
    success_url = "/admin"

    def form_valid(self, form: MeasurementForm):
        form.save()
        return super(MeasurementFormView, self).form_valid(form)
