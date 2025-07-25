# Kanban

This project is a simple Kanban board application.

Each card may store up to eight **custom fields** defined by the company.  In
addition the following fixed fields are available:

* **Título** – basic title of the card
* **Valor negociado** – numeric value (máximo 9.999.999)
* **Conversa** – URL da conversa relacionada
* **ID da Conversa** – identificador textual da conversa
* **Vendedor** – user responsible for the card

## Custom field types

Custom fields can be of type `text`, `number`, `boolean` or `select`.  For a
`select` field you must provide an `options` list with the allowed choices.

Example configuration:

```json
[
  {"name": "Status", "type": "select", "options": ["Novo", "Em andamento", "Fechado"]},
  {"name": "Observacao", "type": "text"}
]
```

Regular users only see cards where they are set as the vendor.  Users with the
`gestor` role can access all cards for their company.  Cards that have no
vendor assigned can be edited or removed by any regular user; the first edit
will automatically set that user as the vendor.

## Front-end JavaScript

All browser-side logic should be stored under `app/static/js/`.  Templates load
these files using `url_for('static', filename='js/kanban.js')`.

## Database migrations

The project uses **Flask-Migrate** to manage database schema changes.

Initialize the migrations directory the first time:

```bash
flask --app run.py db init
```

Create a new migration whenever models change:

```bash
flask --app run.py db migrate -m "Describe your change"
```

Apply migrations and update `instance/kanban.db`:

```bash
flask --app run.py db upgrade
```

To recreate the database from scratch, remove the existing file and run the
upgrade command again:

```bash
rm -f instance/kanban.db
flask --app run.py db upgrade
```
