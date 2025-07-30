# Kanban 5x

Aplicação web de quadro Kanban desenvolvida em Flask. Permite gerenciar cartões, colunas e painéis para múltiplas empresas, com atualização em tempo real via SSE (Server‑Sent Events). O sistema possui um painel de administração para “super‑admins” e autenticação por usuário com diferentes níveis de acesso.

---

## Funcionalidades Principais

- **Quadro Kanban** com múltiplas colunas e cartões arrastáveis.
- **Campos personalizados** por empresa (até 8 campos adicionais) além dos campos fixos: título, valor negociado, conversa (URL), ID da conversa e vendedor responsável.
- **Filtros** de cartões por título, vendedor, valor e data.
- **Modo escuro** configurável por empresa.
- **Atualização em tempo real** utilizando SSE: o endpoint `/events` distribui eventos para os usuários logados na mesma empresa.
- **Papéis de usuário** (`user`, `gestor` e `superadmin`) com permissões distintas:
  - Usuários comuns visualizam apenas os cartões em que são vendedores.
  - Gestores acessam todos os cartões da empresa.
  - Super‑admins têm acesso global e podem trocar de empresa/painel.
- **Webhook Chatwoot** para criação/login automático de usuários a partir de webhooks.
- **API autenticada** para operações em cartões, colunas, painéis e campos personalizados, protegida por token de superadmin.

---

## Estrutura do Projeto

- `app/` – aplicação Flask (modelos, rotas, SSE e utilidades).
- `api/` – endpoints REST para integração externa.
- `migrations/` – gerenciamento de versões do banco (Flask‑Migrate).
- `tests/` – suíte de testes unitários (pytest).
- `instance/` – base SQLite gerada em tempo de execução.
- `run.py` – ponto de entrada da aplicação.

---

## Modelos de Dados (app/models.py)

- **Empresa**: nome, account_id, lista de campos personalizados e configuração de modo escuro.
- **Panel**: conjunto de colunas e usuários vinculados.
- **Usuario**: dados de autenticação/identificação e papel (role).
- **Column**: pertence a um painel e possui cor opcional.
- **Card**: localizado em uma coluna, com campos fixos e dados customizados.

---

## Utilização

### 1. Instalação

1. Crie um ambiente virtual e instale as dependências:

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Defina a variável `SUPERADMIN_TOKEN` com um valor secreto para habilitar as rotas de API e painel de superadmin:

   ```bash
   export SUPERADMIN_TOKEN=supertoken
   ```

3. Inicialize ou atualize o banco de dados:

   ```bash
   flask --app run.py db upgrade
   ```

4. Inicie o servidor de desenvolvimento:

   ```bash
   flask --app run.py run
   ```

A aplicação ficará disponível em `http://localhost:5000/`.

### 2. Fluxo de Acesso

1. Acesse `/login` para realizar autenticação.
2. Usuários comuns visualizam apenas seus cartões; gestores e super‑admins têm visão ampliada.
3. Super‑admins podem acessar `/superadmin?token=SEU_TOKEN` para gerenciar empresas, usuários, painéis e colunas.

### 3. Operações no Quadro

- **Criar coluna**: botão “Adicionar Coluna” no cabeçalho ou via modal (função `add_column` no backend).
- **Editar coluna**: clique sobre a coluna e salve as alterações (`edit_column`).
- **Excluir coluna**: botão “Deletar” na modal de edição (`delete_column`).
- **Criar cartão**: botão “Adicionar Card”, escolhendo a coluna de destino (`add_card`).
- **Editar cartão**: clique no cartão e altere as informações (`edit_card`).
- **Excluir cartão**: na modal de edição clique em “Deletar” (`delete_card`).
- **Mover cartão**: arraste para outra coluna (rota `api_move_card` para AJAX).
- **Escolher painel**: seleção no topo do quadro (rota `select_panel`).
- **Alternar tema**: ícone de sol/luar (rota `toggle_theme`).

Os dados personalizados dos cartões são montados conforme a definição `Empresa.custom_fields` utilizando `build_custom_data`.

### 4. Atualizações em Tempo Real

Enquanto o quadro estiver aberto em vários navegadores, toda criação, edição ou remoção de cartões/colunas e painéis é transmitida instantaneamente através do canal SSE `/events`. O JavaScript processa esses eventos e atualiza a interface automaticamente.

### 5. API REST

Todos os endpoints ficam sob `/api` e exigem o cabeçalho `Authorization: Bearer <SUPERADMIN_TOKEN>`.

Principais rotas:

- **Cards** (`/api/cards`)
  - `GET /api/cards?panel_id=&column_id=&empresa_id=` – lista cartões.
  - `GET /api/cards/<id>` – consulta individual.
  - `POST /api/cards` – cria cartão.
  - `PUT /api/cards/<id>` – atualiza.
  - `DELETE /api/cards/<id>` – remove.
- **Columns** (`/api/columns`) – CRUD similar ao acima.
- **Panels** (`/api/panels`) – CRUD de painéis.
- **Custom Fields** (`/api/custom_fields/<empresa_id>`) – gerenciamento dos campos personalizados de cada empresa.

O endpoint `/api/ping` serve para testar o token (retorna `pong` quando autorizado).

### 6. Painel Super-Admin

Disponível em `/superadmin?token=SEU_TOKEN`. Permite:

- Criar, editar ou remover empresas.
- Gerenciar usuários (vendedores, gestores e super‑admins).
- Criar e organizar painéis e colunas de qualquer empresa.
- Definir os campos personalizados via JSON.

Os formulários utilizam JavaScript (`superadmin.js`) para preencher dinamicamente os campos nas modais.

### 7. Webhook Chatwoot

O endpoint `/webhook/chatwoot` aceita POST (ou GET para testes) com dados como `account_id`, `user_email`, `user_id` e `user_name`. Ele cria a empresa (caso não exista) e um usuário com papel `user`, realizando o login automaticamente e redirecionando para o quadro principal.

---

## Testes

A pasta `tests/` contém cenários de uso e verificação de regras de acesso. Utilize `pytest` para executá-los:

```bash
pytest
```

---

## Dicas

- Arquivos JavaScript localizados em `app/static/js` são incluídos nos templates via `url_for('static', filename='js/kanban.js')`.
- Para efetuar migrações de banco de dados, siga as instruções da seção **Database migrations** do README original.
- O valor máximo permitido para “Valor negociado” em um cartão é definido por `MAX_VALOR_NEGOCIADO` (9.999.999).

---

Este guia apresenta o funcionamento geral do sistema Kanban 5x e os passos necessários para instalação e uso das principais funções. Para personalizações adicionais, consulte o código-fonte e os testes incluídos no projeto.
