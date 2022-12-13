# Generated by Django 4.1 on 2022-12-10 21:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("gcampuscore", "0012_delete_calibration"),
    ]

    operations = [
        migrations.CreateModel(
            name="MeasurementKit",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200, verbose_name="Name")),
                (
                    "short_name",
                    models.CharField(max_length=50, verbose_name="Short name"),
                ),
                (
                    "identifier",
                    models.CharField(max_length=20, verbose_name="Identifier"),
                ),
                (
                    "color",
                    models.CharField(blank=True, max_length=7, verbose_name="Color"),
                ),
            ],
            options={
                "verbose_name": "Measurement kit",
                "verbose_name_plural": "Measurement kits",
            },
        ),
        migrations.CreateModel(
            name="Calibration",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=280, verbose_name="Name")),
                (
                    "calibration_formula",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="Calibration formula"
                    ),
                ),
                (
                    "x_max",
                    models.FloatField(
                        default=-9999, verbose_name="Maximal parameter value"
                    ),
                ),
                (
                    "x_min",
                    models.FloatField(
                        default=-9999, verbose_name="Minimal parameter value"
                    ),
                ),
                (
                    "measurement_kit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="calibrations",
                        to="gcampustools.measurementkit",
                        verbose_name="Measurement kit",
                    ),
                ),
                (
                    "parameter_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="calibrations",
                        to="gcampuscore.parametertype",
                        verbose_name="Parameter",
                    ),
                ),
            ],
            options={
                "verbose_name": "Calibration",
                "verbose_name_plural": "Calibrations",
            },
        ),
    ]