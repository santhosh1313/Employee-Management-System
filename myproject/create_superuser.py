from django.contrib.auth.models import User

username = "Santhosh"
password = "Santhosh#53"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email="santhosh@gmail.com",
        password=password
    )

    print("Superuser created successfully")

else:
    print("Superuser already exists")