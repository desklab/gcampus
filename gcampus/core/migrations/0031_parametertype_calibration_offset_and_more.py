# Generated by Django 4.0.1 on 2022-03-17 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gcampuscore', '0030_alter_measurement_comment_alter_measurement_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='parametertype',
            name='calibration_offset',
            field=models.FloatField(blank=True, default=0, verbose_name='Offset'),
        ),
        migrations.AddField(
            model_name='parametertype',
            name='calibration_slope',
            field=models.FloatField(blank=True, default=1, verbose_name='Slope'),
        ),
        migrations.AlterField(
            model_name='measurement',
            name='comment',
            field=models.TextField(blank=True, help_text='Note on your measurement. This will be publicly visible.', verbose_name='Note'),
        ),
        migrations.AlterField(
            model_name='measurement',
            name='name',
            field=models.CharField(blank=True, help_text='Your forename or team name. This will be publicly visible.', max_length=280, verbose_name='Name'),
        ),
    ]
