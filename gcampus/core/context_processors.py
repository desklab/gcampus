from django.conf import settings


def get_version(request) -> dict:
    return {
        "GCAMPUS_VERSION": settings.GCAMPUS_VERSION
    }
