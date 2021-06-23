__ALL__ = ["MAP_SETTINGS"]

from django.conf import settings

MAP_SETTINGS = dict()

PROJECT_SETTINGS = getattr(settings, "MAP_SETTINGS", {})

MAP_SETTINGS.update(PROJECT_SETTINGS)

