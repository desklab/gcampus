# Generated by Django 4.1 on 2022-10-25 10:53

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.conf import settings
from django.db import migrations

TSVECTOR_CONF = getattr(settings, "TSVECTOR_CONF", "german")


class Migration(migrations.Migration):
    dependencies = [
        ("gcampuscore", "0008_measurement_internal_comment_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="water",
            name="search_vector",
            field=django.contrib.postgres.search.SearchVectorField(
                editable=False, null=True
            ),
        ),
        migrations.AddIndex(
            model_name="water",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["search_vector"], name="gcampuscore_search__de6cca_gin"
            ),
        ),
        migrations.RunSQL(
            f"""
                ALTER TABLE "gcampuscore_water"
                    DROP COLUMN "search_vector" CASCADE,
                    ADD COLUMN "search_vector" tsvector GENERATED ALWAYS AS (
                        setweight(to_tsvector('{TSVECTOR_CONF}', coalesce("name", '')), 'A')
                    ) STORED
            """,
            reverse_sql="",
        ),  # noqa
    ]
