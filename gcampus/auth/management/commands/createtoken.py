from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from gcampus.auth.models import TeacherToken, StudentToken


class Command(BaseCommand):
    help = "Create new tokens"

    def add_arguments(self, parser):
        parser.add_argument('number', type=int)

    def handle(self, *args, **options):
        number = options["number"]
        with transaction.atomic():
            root_token = TeacherToken(teacher_name="GCampus Admin")
            root_token.save()
            print(f"Teacher Token: {root_token.token}")
            for i in range(number):
                token = StudentToken()
                token.parent_token = root_token
                token.save()
                print(f"Token {i + 1:d}: {token.token}")
