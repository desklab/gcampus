#  Copyright (C) 2023 desklab gUG (haftungsbeschränkt)
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

from django.contrib.gis.geos import Point, MultiPoint
from numpy import ndarray, array, unique
from sklearn.cluster import MeanShift


def mean_shift_clustering(
    points: MultiPoint | list[Point],
    bandwidth: float | None = None,
    max_iter: int = 300,
    srid: int = 4326,
) -> tuple[MultiPoint, list[int]]:
    if not isinstance(points, MultiPoint):
        points: MultiPoint = MultiPoint(*points, srid=srid)
    old_srid = points.srid
    meter_srid = 3857
    try:
        points.transform(meter_srid)  # Transform in meters
        model = MeanShift(bandwidth=bandwidth, max_iter=max_iter)
        model.fit(array(points.tuple))
        centroids: ndarray = model.cluster_centers_
        labels: ndarray = model.labels_
        _, counts = unique(labels, return_counts=True)
        clusters = MultiPoint(
            [Point(tuple(centroid)) for centroid in centroids], srid=meter_srid
        )
        clusters.transform(old_srid)
        return clusters, counts
    finally:
        # Reverse transformation to avoid mutating the function's
        # arguments.
        points.transform(old_srid)
