from django.views.generic import ListView


class Measurement_List(ListView):
    model = Measurement
