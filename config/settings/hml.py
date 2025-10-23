# config/settings/hml.py
from .base import *
from decouple import config

# DEBUG é FALSO em homologação
DEBUG = config('DEBUG', default=False, cast=bool)

# Chave secreta (OBRIGATÓRIO vir das variáveis de ambiente)
SECRET_KEY = config('SECRET_KEY')

# O Host do seu app de HML no Render
HML_HOSTNAME = config('HML_HOSTNAME', default='sua-api-hml.onrender.com')
ALLOWED_HOSTS = [HML_HOSTNAME]

# Banco de Dados de HML (ex: seu Aiven gratuito)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}

# Segurança: CSRF (Cross-Site Request Forgery)
# Isso diz ao Django para confiar em requisições vindas do seu próprio site
CSRF_TRUSTED_ORIGINS = [f'https://{HML_HOSTNAME}']