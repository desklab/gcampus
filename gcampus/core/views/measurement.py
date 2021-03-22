from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView

from gcampus.core.forms.measurement import MeasurementForm
from gcampus.core.models import Measurement
from gcampus.core.models import DataPoint


class MeasurementListView(ListView):
    template_name = "gcampuscore/components/measurement_list.html"
    model = Measurement
    context_object_name = "measurement_list"
    paginate_by = 10


class MeasurementDetailView(DetailView):
    model = Measurement
    template_name = "gcampuscore/components/measurement_detail.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)
        # Create any data and add it to the context
        test = DataPoint.objects
        context['datapoint_list'] = DataPoint.objects.all()
        return context

class MeasurementFormView(FormView):
    template_name = "gcampuscore/forms/measurement.html"
    form_class = MeasurementForm
    success_url = "/admin"

    def form_valid(self, form: MeasurementForm):
        form.save()
        return super(MeasurementFormView, self).form_valid(form)
