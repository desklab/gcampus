# Generated by Django 4.0 on 2022-05-05 11:54

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "gcampuscore",
            "0003_alter_measurement_options_alter_measurement_managers_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="measurement",
            name="location",
            field=django.contrib.gis.db.models.fields.PointField(
                help_text="Location of the measurement",
                srid=4326,
                verbose_name="Location",
            ),
        ),
    ]
