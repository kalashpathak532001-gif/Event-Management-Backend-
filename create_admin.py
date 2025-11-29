# create_admin.py
"""
Safe create-superuser script for automated deployments.

It uses environment variables:
 - DJANGO_SUPERUSER_USERNAME
 - DJANGO_SUPERUSER_EMAIL
 - DJANGO_SUPERUSER_PASSWORD

The script inspects the project's AUTH_USER_MODEL and its USERNAME_FIELD.
If required env vars are missing the script will skip creating a superuser
(to avoid failing a build). You can enable strict mode by setting
CREATE_SUPERUSER_STRICT=true in env to fail the build when values are missing.
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", os.getenv("DJANGO_SETTINGS_MODULE", "config.settings"))
django.setup()

from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured

User = get_user_model()
username_field = getattr(User, "USERNAME_FIELD", "username")

# Read env vars
env = os.environ
strict = env.get("CREATE_SUPERUSER_STRICT", "false").lower() in ("1", "true", "yes")

username = env.get("DJANGO_SUPERUSER_USERNAME")  # may be None
email = env.get("DJANGO_SUPERUSER_EMAIL")        # may be None
password = env.get("DJANGO_SUPERUSER_PASSWORD")  # may be None

# Map required field according to USERNAME_FIELD
required_field_name = username_field or "username"
required_value = username if required_field_name == "username" else (email if required_field_name == "email" else None)

def info(msg):
    print("[create_admin] " + msg)

# Validate inputs
if not required_value:
    msg = (
        f"Env var for user model's USERNAME_FIELD ('{required_field_name}') is missing. "
        "Skipping superuser creation."
    )
    if strict:
        raise ImproperlyConfigured(msg)
    info(msg + " (set CREATE_SUPERUSER_STRICT=true to fail instead)")
    sys.exit(0)

if not password:
    msg = "DJANGO_SUPERUSER_PASSWORD is missing. Skipping superuser creation."
    if strict:
        raise ImproperlyConfigured(msg)
    info(msg + " (set CREATE_SUPERUSER_STRICT=true to fail instead)")
    sys.exit(0)

# Build kwargs for create_superuser
create_kwargs = {}
if required_field_name == "username":
    create_kwargs["username"] = username
elif required_field_name == "email":
    create_kwargs["email"] = email
else:
    # fallback: attempt to set both if present
    if username:
        create_kwargs["username"] = username
    if email:
        create_kwargs["email"] = email

# Always provide password
try:
    # If user already exists, skip (avoid duplicate error)
    lookup = {required_field_name: create_kwargs.get(required_field_name)}
    existing = User.objects.filter(**lookup).first()
    if existing:
        info(f"Superuser already exists ({required_field_name}={lookup[required_field_name]}). Skipping.")
        sys.exit(0)

    info(f"Creating superuser with {required_field_name}={create_kwargs.get(required_field_name)}")
    User.objects.create_superuser(password=password, **create_kwargs)
    info("Superuser created.")
except Exception as exc:
    # If strict, fail; otherwise print and continue without failing the build
    msg = f"Failed to create superuser: {exc}"
    if strict:
        raise
    info(msg)
    sys.exit(0)
