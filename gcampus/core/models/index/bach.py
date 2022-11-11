#  Copyright (C) 2021-2022 desklab gUG (haftungsbeschränkt)
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

from __future__ import annotations

__ALL__ = ["BACHIndex"]

from typing import Union

from django.db import models
from django.utils.translation import gettext_lazy as _

from gcampus.core.models.index.base import WaterQualityIndex


class BACHIndex(WaterQualityIndex):
    class Meta:
        verbose_name = _("BACH Index")
        verbose_name_plural = _("BACH Indices")

    measurement = models.OneToOneField(
        "gcampuscore.Measurement",  # noqa
        blank=False,
        null=True,
        on_delete=models.CASCADE,
        related_name="bach_index",
    )

    @classmethod
    def calculate_index(cls, **kwargs) -> float:
        temp_lookup = [
            (14, 100),
            (14.5, 99.5),
            (15, 99),
            (15.5, 98.25),
            (16, 97.5),
            (16.5, 96.25),
            (17, 95),
            (17.5, 92.5),
            (18, 90),
            (18.5, 84.5),
            (19, 79),
            (19.5, 73.25),
            (20, 67.5),
            (20.5, 61.75),
            (21, 56),
            (21.5, 52.5),
            (22, 45),
            (22.5, 39.25),
            (23, 33.5),
            (23.5, 27.75),
            (24, 22),
            (24.5, 18.5),
            (25, 15),
            (25.5, 12),
            (26, 9),
            (26.5, 7.25),
            (27, 5.5),
            (27.5, 4.25),
            (28, 3),
            (28.5, 2.25),
            (29, 1.5),
            (29.5, 1.25),
            (30, 1),
        ]
        if "temp" in kwargs:
            raw = kwargs.get("temp")
            if raw <= 14:
                temp = 100
            elif raw > 30:
                temp = 1
            else:
                for i in range(len(temp_lookup) - 1):
                    if temp_lookup[i][0] < raw <= temp_lookup[i + 1][0]:
                        temp = lin_est(temp_lookup[i], temp_lookup[i + 1], raw)
        else:
            temp = None

        o2_lookup = [
            (0, 2),
            (5, 2.5),
            (10, 3),
            (15, 4.5),
            (20, 6),
            (25, 9),
            (30, 12),
            (35, 15),
            (40, 19),
            (45, 24),
            (50, 30),
            (55, 36),
            (60, 43),
            (65, 53),
            (70, 63),
            (75, 71),
            (80, 79),
            (85, 86),
            (90, 93),
            (95, 99),
            (96, 100),
            (100, 100),
            (105, 100),
            (106, 100),
            (110, 97),
            (115, 95),
            (120, 90.5),
            (125, 87),
            (130, 83),
        ]
        if "o2" in kwargs:
            raw = kwargs.get("o2")
            if raw <= 0:
                o2 = 2
            elif raw > 130:
                o2 = 83
            else:
                for i in range(len(o2_lookup) - 1):
                    if o2_lookup[i][0] < raw <= o2_lookup[i + 1][0]:
                        o2 = lin_est(o2_lookup[i], o2_lookup[i + 1], raw)
        else:
            o2 = None

        bsb5_lookup = [
            (0, 100),
            (0, 5, 99.5),
            (1, 98),
            (1.5, 95),
            (2, 90),
            (2.5, 84),
            (3, 76),
            (3.5, 68),
            (4, 61),
            (4.5, 54),
            (5, 48),
            (5.5, 42),
            (6, 37),
            (7, 28),
            (8, 20.5),
            (9, 14.5),
            (10, 10),
            (15, 4),
        ]
        if "bsb5" in kwargs:
            raw = kwargs.get("bsb5")
            if raw <= 0:
                bsb5 = 100
            elif raw > 15:
                bsb5 = 4
            else:
                for i in range(len(bsb5_lookup) - 1):
                    if bsb5_lookup[i][0] < raw <= bsb5_lookup[i + 1][0]:
                        bsb5 = lin_est(bsb5_lookup[i], bsb5_lookup[i + 1], raw)
        else:
            bsb5 = None

        ph_lookup = [
            (3, 1),
            (3.5, 2.5),
            (4, 7),
            (4.5, 13),
            (5, 22),
            (5.5, 34.5),
            (6, 56.5),
            (6.5, 78.5),
            (6, 6, 83),
            (6.7, 87.5),
            (6.8, 92),
            (6.9, 96),
            (7, 98, 5),
            (7.1, 99.5),
            (7.2, 100),
            (7.3, 100),
            (7.4, 99.5),
            (7.5, 98.5),
            (7.6, 96),
            (7.7, 92),
            (7.8, 87.5),
            (7.9, 83.5),
            (8, 78.5),
            (8.5, 55.5),
            (9, 33),
            (9.5, 18),
            (10, 10.5),
        ]
        if "ph" in kwargs:
            raw = kwargs.get("ph")
            if raw <= 3:
                ph = 1
            elif raw > 10:
                ph = 10.5
            else:
                for i in range(len(ph_lookup) - 1):
                    if ph_lookup[i][0] < raw <= ph_lookup[i + 1][0]:
                        ph = lin_est(ph_lookup[i], ph_lookup[i + 1], raw)
        else:
            ph = None

        no3_lookup = [
            (0, 100),
            (2, 94),
            (4, 88),
            (6, 82),
            (8, 76),
            (10, 70.5),
            (12, 64.5),
            (14, 58.5),
            (16, 52.5),
            (18, 46.5),
            (20, 40.5),
            (22, 35.5),
            (24, 30),
            (26, 26),
            (28, 23),
            (30, 20),
            (36, 15),
            (40, 10),
        ]
        if "no3" in kwargs:
            raw = kwargs.get("no3")
            if raw <= 0:
                no3 = 100
            elif raw > 40:
                no3 = 10
            else:
                for i in range(len(no3_lookup) - 1):
                    if no3_lookup[i][0] < raw <= no3_lookup[i + 1][0]:
                        no3 = lin_est(no3_lookup[i], no3_lookup[i + 1], raw)
        else:
            no3 = None

        po4_lookup = [
            (0, 100),
            (0.1, 95),
            (0.2, 84),
            (0.3, 72),
            (0.4, 60),
            (0.5, 48),
            (0.6, 39),
            (0.7, 31.5),
            (0.8, 25),
            (0.9, 20),
            (1, 16),
            (1.1, 12.5),
            (1.2, 10),
            (1.3, 8),
            (1.4, 7),
            (1.5, 6),
            (1.6, 5.5),
            (1.8, 5),
            (2, 5),
            (2.5, 4),
            (3, 3),
            (4, 2),
            (5, 1),
        ]
        if "po4" in kwargs:
            raw = kwargs.get("po4")
            if raw <= 0:
                po4 = 100
            elif raw > 5:
                po4 = 1
            else:
                for i in range(len(po4_lookup) - 1):
                    if po4_lookup[i][0] < raw <= po4_lookup[i + 1][0]:
                        po4 = lin_est(po4_lookup[i], po4_lookup[i + 1], raw)
        else:
            po4 = None

        nh4_lookup = [
            (0, 100),
            (0, 2, 84),
            (0.4, 60),
            (0.6, 49),
            (0.8, 40),
            (1, 35),
            (1.2, 31),
            (1.4, 28.5),
            (1.6, 26.5),
            (1.8, 24.5),
            (2, 23),
            (2.5, 20),
            (3, 18),
            (4, 15.5),
            (5, 12),
            (6, 10),
            (8, 6.5),
            (10, 4.5),
            (13, 3.5),
        ]
        if "nh4" in kwargs:
            raw = kwargs.get("nh4")
            if raw <= 0:
                nh4 = 100
            elif raw > 13:
                nh4 = 3
            else:
                for i in range(len(nh4_lookup) - 1):
                    if nh4_lookup[i][0] < raw <= nh4_lookup[i + 1][0]:
                        nh4 = lin_est(nh4_lookup[i], nh4_lookup[i + 1], raw)
        else:
            nh4 = None

        conductivity_lookup = [
            (0, 72),
            (25, 85),
            (50, 91),
            (75, 95),
            (100, 97.5),
            (125, 99.5),
            (150, 100),
            (175, 99.5),
            (200, 98.5),
            (225, 97),
            (250, 95.5),
            (275, 93),
            (300, 91),
            (350, 85),
            (400, 77),
            (450, 70),
            (500, 63),
            (550, 56),
            (600, 50),
            (700, 39),
            (800, 31),
            (900, 24),
            (1000, 19),
            (1100, 15),
            (1200, 13),
            (1300, 11),
            (1400, 10),
            (1500, 9),
            (2000, 8),
            (3000, 6),
            (4000, 4),
            (5000, 2),
        ]
        if "conductivity" in kwargs:
            raw = kwargs.get("conductivity")
            if raw <= 0:
                conductivity = 72
            elif raw > 5000:
                conductivity = 2
            else:
                for i in range(len(conductivity_lookup) - 1):
                    if conductivity_lookup[i][0] < raw <= conductivity_lookup[i + 1][0]:
                        conductivity = lin_est(
                            conductivity_lookup[i], conductivity_lookup[i + 1], raw
                        )
        else:
            conductivity = None

        sum_of_weights = 0

        if temp is not None:
            sum_of_weights += 0.08
        if o2 is not None:
            sum_of_weights += 0.20
        if bsb5 is not None:
            sum_of_weights += 0.20
        if ph is not None:
            sum_of_weights += 0.10
        if no3 is not None:
            sum_of_weights += 0.10
        if po4 is not None:
            sum_of_weights += 0.10
        if nh4 is not None:
            sum_of_weights += 0.15
        if conductivity is not None:
            sum_of_weights += 0.07

        index = 1

        if temp is not None:
            index *= temp ** (0.08 / sum_of_weights)
        if o2 is not None:
            index *= o2 ** (0.20 / sum_of_weights)
        if bsb5 is not None:
            index *= bsb5 ** (0.20 / sum_of_weights)
        if ph is not None:
            index *= ph ** (0.10 / sum_of_weights)
        if no3 is not None:
            index *= no3 ** (0.10 / sum_of_weights)
        if po4 is not None:
            index *= po4 ** (0.10 / sum_of_weights)
        if nh4 is not None:
            index *= nh4 ** (0.15 / sum_of_weights)
        if conductivity is not None:
            index *= conductivity ** (0.07 / sum_of_weights)

        return index

    @classmethod
    def calculate_classification(cls, value) -> Union[None, str]:
        if value is not None:
            if value > 83:
                return "I"
            if value > 73:
                return "I-II"
            if value > 56:
                return "II"
            if value > 44:
                return "II-III"
            if value > 27:
                return "III"
            if value > 17:
                return "III-IV"
            if value >= 0:
                return "IV"
        else:
            return None

    @classmethod
    def calculate_description(cls, value) -> Union[None, str]:
        if value is not None:
            if value > 83:
                return "unbelastet"
            if value > 73:
                return "gering belastet"
            if value > 56:
                return "mäßig belastet"
            if value > 44:
                return "kritisch belastet"
            if value > 27:
                return "stark verschmutzt"
            if value > 17:
                return "übermäßig verschmutzt"
            if value >= 0:
                return "übermäßig stark verschmutzt"
        else:
            return None

    @classmethod
    def calculate_validity(cls, parameters) -> float:
        validity: float = 0
        if "temp" in parameters:
            validity += 0.08
        if "o2" in parameters:
            validity += 0.20
        if "bsb5" in parameters:
            validity += 0.20
        if "ph" in parameters:
            validity += 0.10
        if "no3" in parameters:
            validity += 0.10
        if "po4" in parameters:
            validity += 0.10
        if "nh4" in parameters:
            validity += 0.15
        if "conductivity" in parameters:
            validity += 0.07
        return validity


def lin_est(p1, p2, x):
    return p1[1] + (p2[1] - p1[1]) / (p2[0] - p1[0]) * (x - p1[0])
