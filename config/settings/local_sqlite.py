"""Configuração local rápida para desenvolvimento usando SQLite.

Este arquivo é usado apenas pelos checks/migrations automatizados executados
no ambiente de desenvolvimento local do revisor. Ele importa as configurações
base e sobrescreve o `DATABASES` para um banco SQLite simples.
"""
from .base import *

# Segurança / debug para desenvolvimento local
DEBUG = True
SECRET_KEY = 'django-insecure-local-sqlite-key'
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Banco SQLite para testes locais rápidos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email em dev: usa backend console para evitar falhas de envio
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
