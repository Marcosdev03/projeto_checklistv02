#!/bin/bash
# scripts/setup-rds.sh
# Script para configurar a aplicação para usar RDS na EC2

set -e

echo "🚀 Configuração para RDS na EC2"
echo "=================================="
echo ""

# Verificar se está em produção
if [ ! -f ".env.prod" ]; then
    echo "❌ .env.prod não encontrado. Crie-o primeiro com as credenciais do RDS."
    exit 1
fi

echo "📦 Removendo containers antigos..."
docker compose down --remove-orphans

echo "🔄 Reconstruindo imagem Docker..."
docker compose build --no-cache

echo "📝 Aplicando migrações para RDS..."
docker compose up -d app
sleep 5
docker exec -it django_app python manage.py migrate --noinput --settings=config.settings.prod

echo "📂 Coletando arquivos estáticos..."
docker exec -it django_app python manage.py collectstatic --noinput --settings=config.settings.prod

echo "🔍 Executando verificações do Django..."
docker exec -it django_app python manage.py check --settings=config.settings.prod

echo ""
echo "✅ Configuração para RDS concluída!"
echo ""
echo "Próximos passos:"
echo "1. Verificar se os containers estão rodando: docker compose ps"
echo "2. Testar a API: curl http://localhost:8000/api/schema/"
echo "3. Acessar Swagger: http://localhost:8000/api/swagger/"
echo ""
