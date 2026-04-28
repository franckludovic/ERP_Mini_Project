import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from plugins.users_plugin.models import User

username = 'admin'
email = 'admin@gmail.com'
password = 'admin'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        role='admin'
    )
    print(f"Superuser '{username}' created successfully.")
else:
    user = User.objects.get(username=username)
    user.set_password(password)
    user.role = 'admin'
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(f"Superuser '{username}' updated successfully.")
