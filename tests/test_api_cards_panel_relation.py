import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Empresa, Panel, Column, Usuario


def setup_app():
    os.environ['SUPERADMIN_TOKEN'] = 'token'
    return create_app()


def setup_data():
    empresa = Empresa(nome='ACME', account_id='1')
    db.session.add(empresa)
    db.session.commit()
    panel = Panel(name='P', empresa_id=empresa.id)
    db.session.add(panel)
    db.session.commit()
    col = Column(name='Todo', panel_id=panel.id)
    user1 = Usuario(user_id='1', user_email='a@a.com', user_name='A', role='user', empresa_id=empresa.id)
    user2 = Usuario(user_id='2', user_email='b@b.com', user_name='B', role='user', empresa_id=empresa.id)
    panel.usuarios.append(user1)
    db.session.add_all([col, user1, user2])
    db.session.commit()
    return panel, col, user1, user2


def test_vendedor_not_in_panel():
    app = setup_app()
    with app.app_context():
        panel, column, u1, u2 = setup_data()
        client = app.test_client()
        headers = {'Authorization': 'Bearer token'}

        resp = client.post('/api/cards', json={'title': 'x', 'column_id': column.id, 'vendedor_id': u2.id}, headers=headers)
        assert resp.status_code == 400
        assert 'vendedor_id' in resp.get_json()['error']
