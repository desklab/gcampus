from django.urls import path

from gcampus.core.views.measurement import MeasurementFormView

urlpatterns = [
    path("add/", MeasurementFormView.as_view())
]
