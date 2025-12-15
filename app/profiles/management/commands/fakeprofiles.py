from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from faker import Faker

from app.profiles.models import Address, Profile

VALID_ZIP_CODES = [
    "21044600",
    "21740180",
    "21932580",
    "22710807",
    "22763590",
    "22765790",
    "23098190",
    "23560640",
    "23590380",
    "21740120",
    "21932520",
    "22710802",
    "22713168",
    "21044580",
    "21210630",
    "21740150",
    "21932550",
    "21740110",
    "21932500",
    "21932750",
    "22710077",
    "22621160",
    "22621010",
    "22775045",
    "22790600",
    "22795021",
    "22795022",
    "22790720",
    "22790730",
    "21830175",
    "21842490",
    "21810130",
    "21860390",
    "20520000",
    "20550040",
    "20260200",
    "20530010",
    "22710180",
    "22710130",
    "22740180",
    "22723470",
    "21740210",
    "21740320",
    "21741070",
    "21745650",
    "21941250",
    "21941260",
    "21941140",
    "21940490",
    "21040170",
    "21044040",
    "21043090",
    "21042515",
    "22281100",
    "22280020",
    "22281150",
    "22231060",
    "22770420",
    "22773740",
    "22763325",
    "22763580",
    "23055080",
    "23050000",
    "23016620",
    "23045810",
    "21381470",
    "20740610",
    "20756030",
    "21381080",
    "21931593",
    "21931596",
    "21932650",
    "21920310",
    "20211240",
    "20211110",
    "20211120",
    "20081010",
    "20031130",
    "20050000",
    "20221410",
    "20771200",
    "20785180",
    "21670020",
    "23085690",
    "21863600",
    "21866330",
    "21941570",
    "22711300",
    "20785035",
    "21650540",
    "22763601",
    "23026025",
    "23555270",
    "23580540",
    "21044060",
    "21922540",
    "21030030",
    "21236100",
    "21863550",
    "21864230",
]


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
            first_name = _faker.unique.first_name()
            last_name = _faker.unique.last_name()
            username = email = f"{first_name.lower().split()[0]}.{last_name.lower().split()[0]}@example.com"
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
                    type=Profile.TYPE_CLIENT if i % 5 == 0 else Profile.TYPE_INSTRUCTOR,
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
                    zip_code=_faker.random.choice(VALID_ZIP_CODES),
                )
            )

        try:
            Address.objects.bulk_create(addresses)
        except Exception as e:
            raise CommandError(f"Error creating addresses: {e}")
