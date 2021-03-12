from django.urls import path

from gcampus.core.views.measurement import MeasurementFormView
from gcampus.core.views.measurement import MeasurementListView

urlpatterns = [
    path("add/", MeasurementFormView.as_view()),
    path("measurement_list/", MeasurementListView.as_view()),
]
