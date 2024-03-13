import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-jx*nm15*q4#llv1#z1m%^t#o#9x9pxclajm*oo#92@f080&f%_'

DEBUG = True

ALLOWED_HOSTS = []

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}