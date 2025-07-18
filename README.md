# Kanban

This project is a simple Kanban board application.

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