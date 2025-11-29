from django.contrib.auth.hashers import make_password
from django.db import migrations

ADMIN_EMAIL = 'admin@plansync.com'
ADMIN_PASSWORD = 'admin123'


def create_default_admin(apps, schema_editor):
    User = apps.get_model('users', 'User')
    if User.objects.filter(email=ADMIN_EMAIL).exists():
        return
    user = User(
        username=ADMIN_EMAIL,
        email=ADMIN_EMAIL,
        first_name='PlanSync',
        last_name='Admin',
        is_staff=True,
        is_superuser=True,
        is_admin=True,
        password=make_password(ADMIN_PASSWORD),
    )
    user.save()


def remove_default_admin(apps, schema_editor):
    User = apps.get_model('users', 'User')
    User.objects.filter(email=ADMIN_EMAIL).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_admin, remove_default_admin),
    ]
