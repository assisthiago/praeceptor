from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from faker import Faker

from app.profiles.models import Address, Profile


class Command(BaseCommand):
    help = "Create fake user profiles for testing purposes."

    def add_arguments(self, parser):
        parser.add_argument(
            "number",
            type=int,
            help="The number of fake profiles to create.",
        )

    def handle(self, *args, **options):
        connection.ensure_connection()  # Ensure DB connection is alive
        _faker = Faker("pt_BR")

        users = []
        for _ in range(options["number"]):
            first_name = _faker.first_name()
            last_name = _faker.last_name()
            username = email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            users.append(
                User(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=_faker.password(length=18),
                )
            )

        try:
            User.objects.bulk_create(users)
        except Exception as e:
            raise CommandError(f"Error creating users: {e}")

        profiles = []
        for i, user in enumerate(users):
            profiles.append(
                Profile(
                    user=user,
                    type=Profile.TYPE_INSTRUCTOR if i % 5 == 0 else Profile.TYPE_CLIENT,
                    cpf=_faker.random_number(digits=11, fix_len=True),
                    phone=_faker.random_number(digits=11, fix_len=True),
                    birthdate=_faker.date_of_birth(
                        minimum_age=18,
                        maximum_age=50,
                    ),
                )
            )

        try:
            Profile.objects.bulk_create(profiles)
        except Exception as e:
            raise CommandError(f"Error creating profiles: {e}")

        addresses = []
        for profile in profiles:
            addresses.append(
                Address(
                    profile=profile,
                    zip_code=_faker.postcode(),
                )
            )

        try:
            Address.objects.bulk_create(addresses)
        except Exception as e:
            raise CommandError(f"Error creating addresses: {e}")
