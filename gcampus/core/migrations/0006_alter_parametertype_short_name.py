# Generated by Django 4.0.4 on 2022-06-14 15:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("gcampuscore", "0005_measurement_document_cache"),
    ]

    operations = [
        migrations.AlterField(
            model_name="parametertype",
            name="short_name",
            field=models.CharField(
                blank=True, max_length=50, verbose_name="Short name"
            ),
        ),
    ]
