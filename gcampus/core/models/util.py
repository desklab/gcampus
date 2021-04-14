from typing import Union, List, Type, Optional

from django.contrib.postgres.search import SearchVector
from django.db import models
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver

ADMIN_READ_ONLY_FIELDS = ("created_at", "updated_at")

EMPTY = ("", None, False, (), [], {})


class DateModelMixin(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


def get_search_vector(model: Type[models.Model]) -> SearchVector:
    if not hasattr(model, "search_fields"):
        raise ValueError(
            "Model is not correctly setup to support search. A 'search_fields' list or "
            "SearchVector is required!\n"
            "Example: search_fields = [SearchVector('title'), ...]"
        )
    vector: Union[List[SearchVector], SearchVector] = getattr(model, "search_fields")
    if not isinstance(vector, (list, SearchVector)):
        raise ValueError(
            "Unexpected type for 'search_fields'. Expected either SearchVector or list "
            f"but got {type(vector)}"
        )
    if isinstance(vector, list):
        vector: SearchVector = sum(vector[1:], start=vector[0])
    return vector


def update_search_vector(model: models.Model, search_vector: SearchVector):
    temp_field_name = "tmp_search_vector"
    model.objects.annotate(**{
        temp_field_name: search_vector
    }).update(search_vector=F(temp_field_name))


def search_model(model: Type[models.Model]):
    if not hasattr(model, "search_vector"):
        raise ValueError(
            "Model is not correctly setup to support search. "
            "A 'search_vector' field is required!\n"
            "Example: search_vector = SearchVectorField(null=True, editable=False)"
        )
    vector: SearchVector = get_search_vector(model)

    @receiver(post_save, sender=model)
    def _update_search_vector(sender: models.Model, **kwargs):  # noqa
        update_search_vector(sender, vector)

    return model
