# Configuração de Ambientes - Projeto Checklist

## 🚀 Ambientes Disponíveis

### 1️⃣ **DESENVOLVIMENTO LOCAL (ATUAL)** - SQLite
- **Arquivo de Config**: `.env.local`
- **Settings Django**: `config.settings.local_sqlite`
- **Database**: SQLite (arquivo `db.sqlite3` local)
- **Como rodar**:
  ```bash
  docker compose up -d
  ```
- **Endpoints**:
  - API: `http://localhost:8000/api/`
  - Swagger UI: `http://localhost:8000/api/swagger/`
  - Redoc: `http://localhost:8000/api/redoc/`
  - Schema JSON: `http://localhost:8000/api/schema/`

---

### 2️⃣ **PRODUÇÃO NA EC2** - RDS MySQL (PRÓXIMO PASSO)

Quando você provisionar RDS na EC2:

#### Passo 1: Criar `.env.prod` com credenciais RDS
```bash
# .env.prod
DJANGO_SETTINGS_MODULE=config.settings.prod
SECRET_KEY=<gere-uma-chave-segura-aqui>
DEBUG=False
PROD_HOSTNAME=seu-dominio-ou-ip-ec2

# Database RDS (MySQL)
DB_ENGINE=django.db.backends.mysql
DB_NAME=seu_db_name
DB_USER=admin
DB_PASSWORD=sua_senha_rds
DB_HOST=seu-rds-endpoint.amazonaws.com
DB_PORT=3306
DB_ROOT_PASSWORD=sua_senha_root_rds
```

#### Passo 2: Atualizar `docker-compose.yml` para produção
```bash
# Voltará a usar MySQL (não SQLite)
# Será necessário descomentar o serviço `db` no docker-compose
# OU conectar a um RDS externo
```

#### Passo 3: Aplicar migrações
```bash
docker exec -it django_app python manage.py migrate --settings=config.settings.prod
```

#### Passo 4: Coletar arquivos estáticos
```bash
docker exec -it django_app python manage.py collectstatic --noinput --settings=config.settings.prod
```

---

## 📁 Estrutura de Configuração

| Arquivo | Uso | Database |
|---------|-----|----------|
| `.env.local` | Desenvolvimento com Docker | SQLite |
| `.env.prod` | Produção (EC2) | RDS MySQL |
| `config/settings/local_sqlite.py` | Settings para SQLite | SQLite |
| `config/settings/prod.py` | Settings para MySQL | MySQL/RDS |

---

## ✅ Status Atual (Nov 15, 2025)

- ✅ API rodando em `http://localhost:8000`
- ✅ Swagger UI funcional
- ✅ Migrações aplicadas
- ✅ Schema OpenAPI gerado com sucesso
- ✅ Docker Compose com SQLite

---

## 🔧 Comandos Úteis

### Desenvolvimento (Local com Docker)
```bash
# Subir tudo
docker compose up -d

# Ver logs
docker compose logs -f app

# Parar
docker compose down

# Remigrar (se precisar)
docker exec -it django_app python manage.py migrate --settings=config.settings.local_sqlite

# Shell Django
docker exec -it django_app python manage.py shell --settings=config.settings.local_sqlite
```

### Produção (EC2 + RDS) - Quando implementar
```bash
# Subir com config prod
docker compose -f docker-compose.prod.yml up -d

# Migrações
docker exec -it django_app python manage.py migrate --settings=config.settings.prod

# Estáticos
docker exec -it django_app python manage.py collectstatic --noinput --settings=config.settings.prod
```

---

## 🎯 Próximas Ações

1. **Testar a API localmente** com alguns requests
2. **Provisionar RDS na AWS** (MySQL 8.0)
3. **Criar `.env.prod`** com credenciais do RDS
4. **Atualizar docker-compose.prod.yml** para conectar ao RDS
5. **Deploy na EC2** com Gunicorn + Nginx

