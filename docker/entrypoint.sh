#!/usr/bin/env sh
set -e

# Entrada padrão para o container
# Variáveis importantes (padrões):
#   DJANGO_SETTINGS_MODULE (deve ser fornecido pelo ambiente/Render)
#   PORT (padrão 8000)
#   WEB_CONCURRENCY (padrão 1)

DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.prod}"
PORT="${PORT:-8000}"
WEB_CONCURRENCY="${WEB_CONCURRENCY:-1}"

# Opcional: executar migrations se DJANGO_MIGRATE não for 'false'
if [ "${DJANGO_MIGRATE:-true}" != "false" ]; then
  echo "Running migrations (settings=${DJANGO_SETTINGS_MODULE})"
  python manage.py migrate --noinput --settings=${DJANGO_SETTINGS_MODULE}
fi

# Opcional: collectstatic se ENABLE_COLLECTSTATIC definido (padrão false)
if [ "${ENABLE_COLLECTSTATIC:-false}" = "true" ]; then
  echo "Collecting static files"
  python manage.py collectstatic --noinput --settings=${DJANGO_SETTINGS_MODULE}
fi

# Inicia Gunicorn
echo "Starting gunicorn on 0.0.0.0:${PORT} (workers=${WEB_CONCURRENCY})"
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT} --workers ${WEB_CONCURRENCY}
