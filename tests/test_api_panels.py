import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Empresa, Usuario


def setup_app():
    os.environ['SUPERADMIN_TOKEN'] = 'token'
    return create_app()


def setup_data():
    empresa = Empresa(nome='ACME', account_id='1')
    db.session.add(empresa)
    db.session.commit()
    u1 = Usuario(user_id='1', user_email='u1@example.com', user_name='U1', role='user', empresa_id=empresa.id)
    u2 = Usuario(user_id='2', user_email='u2@example.com', user_name='U2', role='gestor', empresa_id=empresa.id)
    db.session.add_all([u1, u2])
    db.session.commit()
    return empresa, u1, u2


def test_panels_crud():
    app = setup_app()
    with app.app_context():
        empresa, u1, u2 = setup_data()
        client = app.test_client()
        headers = {'Authorization': 'Bearer token'}

        # Create
        resp = client.post('/api/panels', json={'name': 'P1', 'empresa_id': empresa.id, 'usuario_ids': [u1.id, u2.id]}, headers=headers)
        assert resp.status_code == 201
        data = resp.get_json()
        panel_id = data['id']
        assert data['name'] == 'P1'
        assert set(data['usuario_ids']) == {u1.id, u2.id}

        # Update
        resp = client.put(f'/api/panels/{panel_id}', json={'name': 'P2', 'usuario_ids': [u1.id]}, headers=headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['name'] == 'P2'
        assert data['usuario_ids'] == [u1.id]

        # List
        resp = client.get('/api/panels', headers=headers)
        assert any(p['id'] == panel_id for p in resp.get_json())

        # Delete
        resp = client.delete(f'/api/panels/{panel_id}', headers=headers)
        assert resp.status_code == 204
        resp = client.get(f'/api/panels/{panel_id}', headers=headers)
        assert resp.status_code == 404
