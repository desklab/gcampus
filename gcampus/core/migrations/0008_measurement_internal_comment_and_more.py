# Generated by Django 4.1 on 2022-08-19 17:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("gcampuscore", "0007_alter_limit_options_alter_calibration_x_max_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="measurement",
            name="internal_comment",
            field=models.TextField(
                blank=True, null=True, verbose_name="internal comment"
            ),
        ),
        migrations.AddField(
            model_name="measurement",
            name="requires_review",
            field=models.BooleanField(default=False, verbose_name="requires review"),
        ),
        migrations.AddField(
            model_name="water",
            name="internal_comment",
            field=models.TextField(
                blank=True, null=True, verbose_name="internal comment"
            ),
        ),
        migrations.AddField(
            model_name="water",
            name="requires_update",
            field=models.BooleanField(default=False, verbose_name="requires update"),
        ),
        migrations.AlterField(
            model_name="measurement",
            name="water",
            field=models.ForeignKey(
                help_text="The water associated with this measurement",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="measurements",
                to="gcampuscore.water",
                verbose_name="Water",
            ),
        ),
    ]
