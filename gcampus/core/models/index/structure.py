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

__ALL__ = ["StructureIndex"]

from typing import Union

from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from gcampus.core.models.index.base import WaterQualityIndex


class UtilizationCategory(models.TextChoices):
    NATURAL = "natural", _("natural forest (deciduous trees)")
    EXTENSIVE = "extensive", _(
        "extensive use: unfertilized or small grazed meadows, no buildings"
    )
    MIXED = "mixed", _("smaller fields, pastures or gardens, coniferous forest")
    INTENSIVE = "intensive", _("intensive farming and arable land, some buildings")
    ARTIFICIAL = "artificial", _("village, industrial area")
    NA = "unknown", _("unknown")


class MarginCategory(models.TextChoices):
    LARGE = "large", _("> 20 m")
    MEDIUM = "medium", _("approx. 5-20 m")
    SMALL = "small", _("approx. 2-5 m")
    TINY = "tiny", _("< 2 m")
    NONE = "none", _("non-existent")
    NA = "unknown", _("unknown")


class CourseCategory(models.TextChoices):
    NATURAL = "natural", _("curved (not modified)")
    CHANGED = "changed", _("partly curved (partly modified)")
    STRETCHED = "stretched", _("stretched (moderately modified)")
    STRAIGHT = "straight", _("straight (strongly modified)")
    ARTIFICIAL = "artificial", _("straight (completely modified)")
    NA = "unknown", _("unknown")


class BankVegetationCategory(models.TextChoices):
    CONTINUOUS = "continuous", _(
        "continuous grove (deciduous trees), several meters wide"
    )
    NARROW = "narrow", _(
        "narrow continuous grove, wet meadow, tall herbaceous plants or reeds"
    )
    SPARSE = "sparse", _(
        "sparse grove, herbaceous vegetation of stinging nettles and other nutrient indicators"
    )
    NON_NATIVE = "non-native", _(
        "individual trees, non-native vegetation (cottonwoods, conifers, or ornamental shrubs), mowed bank"
    )
    ARTIFICIAL = "artificial", _("no trees, no herbaceous vegetation, paved bank")
    NA = "unknown", _("unknown")


class BankStructureCategory(models.TextChoices):
    NATURAL = "natural", _(
        "no fixed banks, many inlets and widenings, water body can expand unhindered in width"
    )
    STRAIGHT = "straight", _(
        "banks straightened, not visibly fixed, some indentations and widenings"
    )
    STRENGTHENED = "strengthened", _(
        "banks partly strengthened (< 50%), bank failures possible"
    )
    FIXED = "fixed", _(
        "banks predominantly strengthened (>50%) by stone fills or wooden piles."
    )
    ARTIFICIAL = "artificial", _(
        "straight bank, steep slope, strengthened (pavement, concrete or similar)"
    )
    NA = "unknown", _("unknown")


class CrossSectionCategory(models.TextChoices):
    VERY_SHALLOW = "very-shallow", _("very shallow (width:depth > 10:1)")
    SHALLOW = "shallow", _("shallow (width:depth approx. 5:1)")
    MODERATE = "moderate", _("moderately deep (width:depth approx. 3:1)")
    DEEP = "deep", _("deep (width:depth approx. 2:1)")
    VERY_DEEP = "very-deep", _("very deep (width:depth < 2:1)")
    NA = "unknown", _("unknown")


class FlowCategory(models.TextChoices):
    MOSAIC = "mosaic", _(
        "mosaic-like, different flow patterns next to and behind each other"
    )
    ALTERNATING = "alternating", _(
        "fast and slow flowing water alternate in close succession"
    )
    INTERVALS = "intervals", _(
        "alternation of slow and fast flowing water at longer intervals"
    )
    MIXED = "mixed", _("alternation of slow and fast flowing water recognizable")
    UNIFORM = "uniform", _("uniform flowing water")
    NA = "unknown", _("unknown")


class DepthVarianceCategory(models.TextChoices):
    MOSAIC = "mosaic", _("mosaic-like alternation between deep and shallow water areas")
    MAJOR = "major", _("major depth variance")
    MODERATE = "moderate", _("moderate depth variance")
    MINOR = "minor", _("minor depth variance")
    UNIFORM = "uniform", _("no depth variance")
    NA = "unknown", _("unknown")


class RiverbedCategory(models.TextChoices):
    MOSAIC = "mosaic", _(
        "mosaic-like distribution of sand/gravel/stones and deadwood, pronounced formation of islands"
    )
    DIVERSE = "diverse", _(
        "diversified riverbed (sand/gravel/stones/deadwood), rudimentary formation of islands"
    )
    INTERVALS = "intervals", _(
        "more uniform riverbed, different structures at greater intervals"
    )
    MIXED = "mixed", _("silted/paved/concreted riverbed over long stretches")
    UNIFORM = "uniform", _("uniform riverbed, completely silted/paved/concreted")
    NA = "unknown", _("unknown")


class ContinuityCategory(models.TextChoices):
    NATURAL = "natural", _("no obstacles, natural waterfall/cascade")
    STEP = "step", _(
        "piping < 2 m, artificial step of single stones, can be overcome by fish and invertebrates"
    )
    OBSTACLE = "obstacle", _(
        "piping 2-5m, minor step (< 30 cm), can be overcome by fish, fish ladder"
    )
    HINDRANCE = "hindrance", _("piping 5-10m, major step or other barriers (30-100 cm)")
    BLOCKED = "blocked", _("piping > 10 m, step or other barriers > 100 cm")
    NA = "unknown", _("unknown")


class StructureIndex(WaterQualityIndex):
    class Meta:
        verbose_name = _("Physical-Structural Index")
        verbose_name_plural = _("Physical-Structural Indices")

    measurement = models.OneToOneField(
        "gcampuscore.Measurement",  # noqa
        blank=False,
        null=True,
        on_delete=models.CASCADE,
        related_name="structure_index",
    )

    utilization = models.CharField(
        max_length=20,
        choices=UtilizationCategory.choices,
        default=UtilizationCategory.NA,
        verbose_name=_("Environment utilization"),
    )

    margin = models.CharField(
        max_length=20,
        choices=MarginCategory.choices,
        default=MarginCategory.NA,
        verbose_name=_("Margin width"),
    )

    course = models.CharField(
        max_length=20,
        choices=CourseCategory.choices,
        default=CourseCategory.NA,
        verbose_name=_("Water course"),
    )

    bank_vegetation = models.CharField(
        max_length=20,
        choices=BankVegetationCategory.choices,
        default=BankVegetationCategory.NA,
        verbose_name=_("Water bank vegetation"),
    )

    bank_structure = models.CharField(
        max_length=20,
        choices=BankStructureCategory.choices,
        default=BankStructureCategory.NA,
        verbose_name=_("Water bank structure"),
    )

    cross_section = models.CharField(
        max_length=20,
        choices=CrossSectionCategory.choices,
        default=CrossSectionCategory.NA,
        verbose_name=_("Water cross-section"),
    )

    flow = models.CharField(
        max_length=20,
        choices=FlowCategory.choices,
        default=FlowCategory.NA,
        verbose_name=_("Water flow pattern"),
    )

    depth_variance = models.CharField(
        max_length=20,
        choices=DepthVarianceCategory.choices,
        default=DepthVarianceCategory.NA,
        verbose_name=_("Variance of water depth"),
    )

    riverbed = models.CharField(
        max_length=20,
        choices=RiverbedCategory.choices,
        default=RiverbedCategory.NA,
        verbose_name=_("Riverbed"),
    )

    continuity = models.CharField(
        max_length=20,
        choices=ContinuityCategory.choices,
        default=ContinuityCategory.NA,
        verbose_name=_("Continuity"),
    )

    def save(self, **kwargs):
        self._update_value(commit=False)
        self._update_classification(commit=False)
        self._update_description(commit=False)
        self._update_validity(commit=False)
        return super(StructureIndex, self).save(**kwargs)

    def _update_value(self, commit=True):
        self.value = self.calculate_index(self)
        if commit:
            self.save()

    def _update_validity(self, commit=True):
        self.validity = self.calculate_validity(self)
        if commit:
            self.save()

    @classmethod
    def calculate_index(cls, instance) -> float:
        parameter_sum = 0
        parameter_count = 0

        if instance.utilization != UtilizationCategory.NA:
            parameter_count += 1
        if instance.utilization == UtilizationCategory.NATURAL:
            parameter_sum += 1
        elif instance.utilization == UtilizationCategory.EXTENSIVE:
            parameter_sum += 2
        elif instance.utilization == UtilizationCategory.MIXED:
            parameter_sum += 3
        elif instance.utilization == UtilizationCategory.INTENSIVE:
            parameter_sum += 4
        elif instance.utilization == UtilizationCategory.ARTIFICIAL:
            parameter_sum += 5

        if instance.margin != MarginCategory.NA:
            parameter_count += 1
        if instance.margin == MarginCategory.LARGE:
            parameter_sum += 1
        elif instance.margin == MarginCategory.MEDIUM:
            parameter_sum += 2
        elif instance.margin == MarginCategory.SMALL:
            parameter_sum += 3
        elif instance.margin == MarginCategory.TINY:
            parameter_sum += 4
        elif instance.margin == MarginCategory.NONE:
            parameter_sum += 5

        if instance.course != CourseCategory.NA:
            parameter_count += 1
        if instance.course == CourseCategory.NATURAL:
            parameter_sum += 1
        elif instance.course == CourseCategory.CHANGED:
            parameter_sum += 2
        elif instance.course == CourseCategory.STRETCHED:
            parameter_sum += 3
        elif instance.course == CourseCategory.STRAIGHT:
            parameter_sum += 4
        elif instance.course == CourseCategory.ARTIFICIAL:
            parameter_sum += 5

        if instance.bank_vegetation != BankVegetationCategory.NA:
            parameter_count += 1
        if instance.bank_vegetation == BankVegetationCategory.CONTINUOUS:
            parameter_sum += 1
        elif instance.bank_vegetation == BankVegetationCategory.NARROW:
            parameter_sum += 2
        elif instance.bank_vegetation == BankVegetationCategory.SPARSE:
            parameter_sum += 3
        elif instance.bank_vegetation == BankVegetationCategory.NON_NATIVE:
            parameter_sum += 4
        elif instance.bank_vegetation == BankVegetationCategory.ARTIFICIAL:
            parameter_sum += 5

        if instance.bank_structure != BankStructureCategory.NA:
            parameter_count += 1
        if instance.bank_structure == BankStructureCategory.NATURAL:
            parameter_sum += 1
        elif instance.bank_structure == BankStructureCategory.STRAIGHT:
            parameter_sum += 2
        elif instance.bank_structure == BankStructureCategory.STRENGTHENED:
            parameter_sum += 3
        elif instance.bank_structure == BankStructureCategory.FIXED:
            parameter_sum += 4
        elif instance.bank_structure == BankStructureCategory.ARTIFICIAL:
            parameter_sum += 5

        if instance.cross_section != CrossSectionCategory.NA:
            parameter_count += 1
        if instance.cross_section == CrossSectionCategory.VERY_SHALLOW:
            parameter_sum += 1
        elif instance.cross_section == CrossSectionCategory.SHALLOW:
            parameter_sum += 2
        elif instance.cross_section == CrossSectionCategory.MODERATE:
            parameter_sum += 3
        elif instance.cross_section == CrossSectionCategory.DEEP:
            parameter_sum += 4
        elif instance.cross_section == CrossSectionCategory.VERY_DEEP:
            parameter_sum += 5

        if instance.flow != FlowCategory.NA:
            parameter_count += 1
        if instance.flow == FlowCategory.MOSAIC:
            parameter_sum += 1
        elif instance.flow == FlowCategory.ALTERNATING:
            parameter_sum += 2
        elif instance.flow == FlowCategory.INTERVALS:
            parameter_sum += 3
        elif instance.flow == FlowCategory.MIXED:
            parameter_sum += 4
        elif instance.flow == FlowCategory.UNIFORM:
            parameter_sum += 5

        if instance.depth_variance != DepthVarianceCategory.NA:
            parameter_count += 1
        if instance.depth_variance == DepthVarianceCategory.MOSAIC:
            parameter_sum += 1
        elif instance.depth_variance == DepthVarianceCategory.MAJOR:
            parameter_sum += 2
        elif instance.depth_variance == DepthVarianceCategory.MODERATE:
            parameter_sum += 3
        elif instance.depth_variance == DepthVarianceCategory.MINOR:
            parameter_sum += 4
        elif instance.depth_variance == DepthVarianceCategory.UNIFORM:
            parameter_sum += 5

        if instance.riverbed != RiverbedCategory.NA:
            parameter_count += 1
        if instance.riverbed == RiverbedCategory.MOSAIC:
            parameter_sum += 1
        elif instance.riverbed == RiverbedCategory.DIVERSE:
            parameter_sum += 2
        elif instance.riverbed == RiverbedCategory.INTERVALS:
            parameter_sum += 3
        elif instance.riverbed == RiverbedCategory.MIXED:
            parameter_sum += 4
        elif instance.riverbed == RiverbedCategory.UNIFORM:
            parameter_sum += 5

        if instance.continuity != ContinuityCategory.NA:
            parameter_count += 1
        if instance.continuity == ContinuityCategory.NATURAL:
            parameter_sum += 1
        elif instance.continuity == ContinuityCategory.STEP:
            parameter_sum += 2
        elif instance.continuity == ContinuityCategory.OBSTACLE:
            parameter_sum += 3
        elif instance.continuity == ContinuityCategory.HINDRANCE:
            parameter_sum += 4
        elif instance.continuity == ContinuityCategory.BLOCKED:
            parameter_sum += 5

        if parameter_count > 0:
            index: float = parameter_sum / parameter_count
            return index
        else:
            return None

    @classmethod
    def calculate_classification(cls, value) -> Union[None, str]:
        if value is not None:
            if value <= 1.5:
                return "I"
            if value <= 2.5:
                return "II"
            if value <= 3.5:
                return "III"
            if value <= 4.5:
                return "IV"
            if value <= 5:
                return "V"
        else:
            return None

    @classmethod
    def calculate_description(cls, value) -> Union[None, str]:
        if value is not None:
            if value <= 1.5:
                return "natürlich"
            if value <= 2.5:
                return "naturnah"
            if value <= 3.5:
                return "verändert"
            if value <= 4.5:
                return "beeinträchtigt"
            if value <= 5:
                return "geschädigt"
        else:
            return None

    @classmethod
    def calculate_validity(cls, instance) -> float:
        validity: float = 0

        if instance.utilization != UtilizationCategory.NA:
            validity += 0.1
        if instance.margin != MarginCategory.NA:
            validity += 0.1
        if instance.course != CourseCategory.NA:
            validity += 0.1
        if instance.bank_vegetation != BankVegetationCategory.NA:
            validity += 0.1
        if instance.bank_structure != BankStructureCategory.NA:
            validity += 0.1
        if instance.cross_section != CrossSectionCategory.NA:
            validity += 0.1
        if instance.flow != FlowCategory.NA:
            validity += 0.1
        if instance.depth_variance != DepthVarianceCategory.NA:
            validity += 0.1
        if instance.riverbed != RiverbedCategory.NA:
            validity += 0.1
        if instance.continuity != ContinuityCategory.NA:
            validity += 0.1

        return validity
