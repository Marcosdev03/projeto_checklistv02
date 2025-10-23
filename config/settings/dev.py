# config/settings/dev.py
from .base import *
from decouple import config

# DEBUG é VERDADEIRO em desenvolvimento
DEBUG = config('DEBUG', default=True, cast=bool)

# Chave secreta (pode ser simples em dev, mas vamos ler do .env)
SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-fallback')

# Hosts permitidos em DEV
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Banco de dados local (SQLite ou MySQL Local)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='db_checklist_dev'),
        'USER': config('DB_USER', default='root'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='127.0.0.1'),
        'PORT': config('DB_PORT', default='3306'),
    }
}