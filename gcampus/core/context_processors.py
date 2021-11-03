from django.conf import settings

def get_version(request):
    return {'GCAMPUS_VERSION':settings.GCAMPUS_VERSION}