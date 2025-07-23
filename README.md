# Kanban

This project is a simple Kanban board application.

Each card may store up to eight **custom fields** defined by the company.  In
addition the following fixed fields are available:

* **Título** – basic title of the card
* **Valor negociado** – numeric value
* **Vendedor** – user responsible for the card

Regular users only see cards where they are set as the vendor.  Users with the
`gestor` role can access all cards for their company.

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
