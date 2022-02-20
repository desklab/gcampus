# Generated by Django 4.0 on 2022-01-04 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gcampusauth", "0011_coursetoken_overview_document"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="accesskey",
            options={"ordering": ("created_at",), "verbose_name": "Access key"},
        ),
        migrations.AlterModelOptions(
            name="coursetoken",
            options={"verbose_name": "Course token"},
        ),
        migrations.AlterField(
            model_name="coursetoken",
            name="school_name",
            field=models.CharField(
                blank=True, max_length=140, verbose_name="Name of school"
            ),
        ),
        migrations.AlterField(
            model_name="coursetoken",
            name="teacher_email",
            field=models.EmailField(max_length=254, verbose_name="email"),
        ),
        migrations.AlterField(
            model_name="coursetoken",
            name="teacher_name",
            field=models.CharField(
                blank=True, max_length=140, verbose_name="Name of teacher"
            ),
        ),
        migrations.AlterField(
            model_name="coursetoken",
            name="token_name",
            field=models.CharField(
                blank=True, max_length=30, verbose_name="Name of course"
            ),
        ),
    ]
