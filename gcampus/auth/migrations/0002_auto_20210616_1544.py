# Generated by Django 3.1.7 on 2021-06-16 13:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("gcampuscore", "0021_update_search"),
        ("gcampusauth", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="StudentToken",
            new_name="AccessKey",
        ),
        migrations.RenameModel(
            old_name="TeacherToken",
            new_name="CourseToken",
        ),
        migrations.AlterModelOptions(
            name="accesskey",
            options={"verbose_name": "Access Key"},
        ),
        migrations.AlterModelOptions(
            name="coursetoken",
            options={"verbose_name": "Course Token"},
        ),
    ]
