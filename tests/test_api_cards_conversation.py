import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Empresa, Usuario, Column, Card, Panel


def setup_app():
    os.environ['SUPERADMIN_TOKEN'] = 'token'
    return create_app()


def setup_basic():
    empresa = Empresa(nome='ACME', account_id='1')
    db.session.add(empresa)
    db.session.commit()
    panel = Panel(name='Main', empresa_id=empresa.id)
    column = Column(name='Todo', panel_id=panel.id)
    usuario = Usuario(user_id='1', user_email='u@example.com', user_name='U', role='gestor', empresa_id=empresa.id)
    db.session.add_all([panel, column, usuario])
    db.session.commit()
    return empresa, column, usuario


def test_get_by_conversation_id():
    app = setup_app()
    with app.app_context():
        empresa, column, user = setup_basic()
        card = Card(title='x', column_id=column.id, vendedor_id=user.id, conversation_id='abc')
        db.session.add(card)
        db.session.commit()

        client = app.test_client()
        headers = {'Authorization': 'Bearer token'}

        resp = client.get('/api/cards/by_conversation/abc', headers=headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['id'] == card.id
        assert data['conversation_id'] == 'abc'

        resp = client.get('/api/cards/by_conversation/zzz', headers=headers)
        assert resp.status_code == 404
