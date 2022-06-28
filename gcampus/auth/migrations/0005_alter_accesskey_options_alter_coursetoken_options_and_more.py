# Generated by Django 4.0 on 2022-06-28 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("gcampusauth", "0004_alter_accesskey_options"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="accesskey",
            options={
                "ordering": ("created_at", "token"),
                "verbose_name": "Access key",
                "verbose_name_plural": "Access keys",
            },
        ),
        migrations.AlterModelOptions(
            name="coursetoken",
            options={
                "verbose_name": "Course token",
                "verbose_name_plural": "Course tokens",
            },
        ),
        migrations.AlterField(
            model_name="accesskey",
            name="permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Specific permissions for this access key.",
                related_name="access_key_set",
                related_query_name="access_key",
                to="auth.Permission",
                verbose_name="access key permissions",
            ),
        ),
        migrations.AlterField(
            model_name="coursetoken",
            name="permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Specific permissions for this course token.",
                related_name="course_token_set",
                related_query_name="course_token",
                to="auth.Permission",
                verbose_name="course token permissions",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="groups",
            field=models.ManyToManyField(
                blank=True,
                help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                related_name="user_set",
                related_query_name="user",
                to="auth.Group",
                verbose_name="groups",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="user_permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Specific permissions for this user.",
                related_name="user_set",
                related_query_name="user",
                to="auth.Permission",
                verbose_name="user permissions",
            ),
        ),
    ]
