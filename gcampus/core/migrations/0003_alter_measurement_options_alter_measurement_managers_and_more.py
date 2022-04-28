# Generated by Django 4.0.1 on 2022-04-28 18:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gcampuscore", "0002_search"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="measurement",
            options={
                "default_manager_name": "objects",
                "ordering": ("created_at", "name"),
                "verbose_name": "Measurement",
                "verbose_name_plural": "Measurements",
            },
        ),
        migrations.AlterModelManagers(
            name="measurement",
            managers=[],
        ),
        migrations.RemoveField(
            model_name="parametertype",
            name="calibration_formula",
        ),
        migrations.AddField(
            model_name="parametertype",
            name="color",
            field=models.CharField(blank=True, max_length=7, verbose_name="Color"),
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
                (
                    "name",
                    models.CharField(blank=True, max_length=280, verbose_name="Name"),
                ),
                (
                    "calibration_formula",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="Calibration formula"
                    ),
                ),
                (
                    "x_max",
                    models.FloatField(default=-9999, verbose_name="Maximal x value"),
                ),
                (
                    "x_min",
                    models.FloatField(default=-9999, verbose_name="Minimal x value"),
                ),
                (
                    "calibration_parameter_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="calibration_parameter",
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
