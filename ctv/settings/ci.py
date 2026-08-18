from ctv.settings.base import *  # noqa F403


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-jr3^jk4c*r*goat!a=4nm_1wm5l_xf=6ywsu6)243wwdwsswzc"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []
# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "ctv",
        "USER": "ctv_django",
        "PASSWORD": "ctv_django",
        "HOST": "127.0.0.1",  # Use 'localhost' or your server's IP address
        "PORT": "3306",  # Default MySQL port
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
