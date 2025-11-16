# Frontend (React + Vite)

Este diretório contém um pequeno frontend React (Vite) com o componente de Login/Cadastro que você forneceu.

Como usar (desenvolvimento):

1. Vá para a pasta `frontend`:

```bash
cd frontend
```

2. Instale dependências:

```bash
npm install
```

3. Rode em modo desenvolvedor:

```bash
npm run dev
```

O Vite iniciará um servidor (por padrão em `http://localhost:5173`). O `index.html` já carrega o Tailwind via CDN para que as classes utilitárias que você usou funcionem rapidamente.

Observações:
- Em produção você pode integrar essa pasta ao processo de build do seu deploy (build estático com `npm run build`).
- O Tailwind está sendo carregado via CDN para facilitar o desenvolvimento rápido; se quiser usar Tailwind no pipeline de build, adicione a configuração e dependências do Tailwind.
