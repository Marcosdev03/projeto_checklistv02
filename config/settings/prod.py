# config/settings/prod.py
from .base import *
from decouple import config

# DEBUG é FALSO em produção (NUNCA mude isso)
DEBUG = False

# Chave secreta (OBRIGATÓRIO vir das variáveis de ambiente)
SECRET_KEY = config('SECRET_KEY')

# O Host do seu app de PROD no Render
PROD_HOSTNAME = config('PROD_HOSTNAME', default='sua-api-prod.onrender.com')
ALLOWED_HOSTS = [PROD_HOSTNAME]

# Banco de Dados de PROD (ex: um banco Aiven pago ou um AWS RDS)
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

# Segurança: CSRF
CSRF_TRUSTED_ORIGINS = [f'https://{PROD_HOSTNAME}']

# Desabilita a documentação da API em produção
SPECTACULAR_SETTINGS['SERVE_INCLUDE_SCHEMA'] = False