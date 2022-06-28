# Generated by Django 4.0 on 2022-06-28 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gcampuscore", "0006_alter_parametertype_short_name"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="limit",
            options={"verbose_name": "Limit", "verbose_name_plural": "Limits"},
        ),
        migrations.AlterField(
            model_name="calibration",
            name="x_max",
            field=models.FloatField(
                default=-9999, verbose_name="Maximal parameter value"
            ),
        ),
        migrations.AlterField(
            model_name="calibration",
            name="x_min",
            field=models.FloatField(
                default=-9999, verbose_name="Minimal parameter value"
            ),
        ),
    ]
