# Generated by Django 4.1 on 2022-11-25 14:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "gcampuscore",
            "0010_bachindex_saprobicindex_structureindex_trophicindex_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="measurement",
            name="data_quality_warning",
            field=models.BooleanField(
                default=False, verbose_name="data quality warning"
            ),
        ),
        migrations.AddField(
            model_name="parametertype",
            name="lower_warning_limit",
            field=models.FloatField(
                blank=True, null=True, verbose_name="lower warning limit"
            ),
        ),
        migrations.AddField(
            model_name="parametertype",
            name="upper_warning_limit",
            field=models.FloatField(
                blank=True, null=True, verbose_name="upper warning limit"
            ),
        ),
    ]
