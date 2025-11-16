# Projeto Checklist (Arquivo de Encerramento)

Aviso: Este repositório está encerrado pelo autor por falta de conhecimento técnico para continuar o desenvolvimento.

Este projeto era uma aplicação Django + React (Vite) para gerenciar checklists/tarefas. Ele contém:

- Backend: Django (com Django REST Framework) e endpoints REST em `api/`.
- Frontend: aplicação React construída com Vite em `frontend/`.
- Containerização: `Dockerfile`, `docker-compose.yml` e `docker-compose.prod.yml`.
- Configurações e settings em `config/`.

## Motivo do encerramento

Por falta de conhecimento e por não conseguir dar continuidade ao projeto no momento, decidi encerrar/arquivar este repositório. Não é um problema técnico insolúvel — apenas uma decisão pessoal de interromper o trabalho aqui.

## O que está disponível

- Código-fonte completo do backend (Django) e do frontend (React) no repositório.
- Endpoints principais:
  - Registro: POST `/api/usuarios/`
  - Token JWT: POST `/api/token/`, POST `/api/token/refresh/`
  - Tarefas: CRUD em `/api/tarefas/` (requer autenticação JWT)
  - Documentação (quando em DEBUG): `/api/swagger/` e `/api/schema/`
- Recursos para executar localmente: `manage.py`, `requirements.txt`, `frontend/package.json`.

## Se alguém quiser retomar

Fique à vontade para clonar este repositório, criar uma branch e continuar o trabalho. Algumas sugestões para quem for continuar:

1. Rodar o backend localmente com o ambiente virtual Python e o SQLite já incluso:

   1. Crie e ative um venv, instale dependências:

      ```bash
      python -m venv .venv
      source .venv/bin/activate
      pip install -r requirements.txt
      ```

   2. Rodar migrações e criar superuser (opcional):

      ```bash
      python manage.py migrate
      python manage.py createsuperuser
      ```

   3. Rodar servidor local:

      ```bash
      python manage.py runserver
      ```

2. Rodar frontend (opcional durante desenvolvimento):

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. Para produzir os assets estáticos e integrar ao Django (fluxo já usado no projeto):

   ```bash
   cd frontend
   npm run build
   cp -r dist ../staticfiles/frontend
   python manage.py collectstatic --noinput
   ```

## Notas finais

Se você estiver lendo isto e quiser continuar, peço apenas que abra um pull request com as mudanças e, se possível, deixe uma nota explicando como você pretende seguir (melhorias prioritárias, refatorações, testes, etc.).

Obrigado por olhar o código — lamento não poder levar este projeto adiante no momento.

— O autor
