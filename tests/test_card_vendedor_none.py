import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import g

from app import create_app, db
from app.models import Empresa, Usuario, Column, Card, Panel


def setup_basic_data():
    empresa = Empresa(nome='ACME', account_id='1')
    db.session.add(empresa)
    db.session.commit()
    usuario = Usuario(user_id='1', user_email='u@example.com', user_name='U', role='user', empresa_id=empresa.id)
    panel = Panel(name='Main', empresa_id=empresa.id)
    column = Column(name='Todo', panel_id=panel.id)
    db.session.add_all([usuario, panel, column])
    db.session.commit()
    return usuario, column


def test_edit_and_delete_card_vendedor_none():
    app = create_app()
    with app.app_context():
        user, column = setup_basic_data()
        card_edit = Card(title='old', column_id=column.id)
        card_delete = Card(title='del', column_id=column.id)
        db.session.add_all([card_edit, card_delete])
        db.session.commit()

        g.user = user
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['vendedor_id'] = user.id
            sess['empresa_id'] = user.empresa_id

        # Edit card with vendedor_id None
        resp = client.post(f'/edit_card/{card_edit.id}', data={'title': 'new'})
        assert resp.status_code == 302
        db.session.refresh(card_edit)
        assert card_edit.title == 'new'
        assert card_edit.vendedor_id == user.id

        # Delete card with vendedor_id None
        resp = client.post(f'/delete_card/{card_delete.id}')
        assert resp.status_code == 204
        assert Card.query.get(card_delete.id) is None
