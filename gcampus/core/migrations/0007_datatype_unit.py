# Generated by Django 3.1.7 on 2021-04-05 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gcampuscore", "0006_auto_20210405_1921"),
    ]

    operations = [
        migrations.AddField(
            model_name="datatype",
            name="unit",
            field=models.CharField(blank=True, max_length=10, verbose_name="Unit"),
        ),
    ]
