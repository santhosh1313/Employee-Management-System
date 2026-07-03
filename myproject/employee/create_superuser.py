import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "myproject.settings"
)

django.setup()

from django.contrib.auth.models import User

username = "Santhosh"
password = "Santhosh#53"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email="admin@gmail.com",
        password=password
    )
    print("Superuser created")
else:
    print("Superuser already exists")