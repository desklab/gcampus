# Generated by Django 4.0.3 on 2022-04-08 10:56
import django.db.models.deletion
from celery.utils import noop
from django.db import migrations, models, transaction


def create_courses(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Course = apps.get_model("gcampusauth", "Course")  # noqa
    CourseToken = apps.get_model("gcampusauth", "CourseToken")  # noqa
    with transaction.atomic():
        for course_token in CourseToken.objects.all():
            course = Course.objects.using(db_alias).create(
                name=course_token.token_name,
                school_name=course_token.school_name,
                teacher_name=course_token.token_name,
                teacher_email=course_token.token_name,
                overview_document=course_token.overview_document,
            )
            course_token.course = course
            course_token.save()
            course.access_keys.set(course_token.access_keys.all())


class Migration(migrations.Migration):
    dependencies = [
        ("gcampusauth", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Course",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "name",
                    models.CharField(
                        blank=True, max_length=30, verbose_name="Name of course"
                    ),
                ),
                (
                    "school_name",
                    models.CharField(
                        blank=True, max_length=140, verbose_name="Name of school"
                    ),
                ),
                (
                    "teacher_name",
                    models.CharField(
                        blank=True, max_length=140, verbose_name="Name of teacher"
                    ),
                ),
                (
                    "teacher_email",
                    models.EmailField(max_length=254, verbose_name="email"),
                ),
                (
                    "overview_document",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="documents/course/overview",
                        verbose_name="Overview Document",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="accesskey",
            name="course",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="access_keys",
                to="gcampusauth.course",
            ),
        ),
        migrations.AddField(
            model_name="coursetoken",
            name="course",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="course_tokens",
                to="gcampusauth.course",
            ),
        ),
        migrations.RunPython(
            create_courses,
            reverse_code=noop,  # Do nothing as the model is deleted anyway
        ),
        migrations.AlterField(
            model_name="accesskey",
            name="course",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="access_keys",
                to="gcampusauth.course",
            ),
        ),
        migrations.AlterField(
            model_name="coursetoken",
            name="course",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="course_tokens",
                to="gcampusauth.course",
            ),
        ),
        migrations.RemoveField(
            model_name="accesskey",
            name="parent_token",
        ),
        migrations.RemoveField(
            model_name="coursetoken",
            name="overview_document",
        ),
        migrations.RemoveField(
            model_name="coursetoken",
            name="school_name",
        ),
        migrations.RemoveField(
            model_name="coursetoken",
            name="teacher_email",
        ),
        migrations.RemoveField(
            model_name="coursetoken",
            name="teacher_name",
        ),
        migrations.RemoveField(
            model_name="coursetoken",
            name="token_name",
        ),
    ]
