#  Copyright (C) 2021 desklab gUG (haftungsbeschränkt)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from django.urls import path, include

from gcampus.analysis.apps import GCampusAnalysisAppConfig

from gcampus.analysis.views import analysis, analysis_measurement

# Necessary to get the plots to work
from gcampus.analysis.dash_apps import Example_Measurement


# Turn off black formatting and pylint
# fmt: off
# pylint: disable=line-too-long
urlpatterns = [
    path("analysis/example/plotly", analysis, name="analysis"),
    path("analysis/parameters", analysis_measurement, name="analysis_measure"),
]
# fmt: on
# pylint: enable=line-too-long

app_name = GCampusAnalysisAppConfig.label
