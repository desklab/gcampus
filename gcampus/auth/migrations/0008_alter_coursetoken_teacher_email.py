# Generated by Django 3.2.8 on 2021-11-17 00:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gcampusauth", "0007_auto_20211031_1155"),
    ]

    operations = [
        migrations.AlterField(
            model_name="coursetoken",
            name="teacher_email",
            field=models.EmailField(max_length=254, verbose_name="E-Mail Address"),
        ),
    ]