import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Empresa


def setup_app():
    os.environ['SUPERADMIN_TOKEN'] = 'token'
    app = create_app()
    return app


def create_empresa():
    empresa = Empresa(nome='ACME', account_id='1')
    db.session.add(empresa)
    db.session.commit()
    return empresa


def test_columns_crud():
    app = setup_app()
    with app.app_context():
        empresa = create_empresa()
        client = app.test_client()
        headers = {'SUPERADMIN_TOKEN': 'token'}

        # Create
        resp = client.post('/api/columns', json={'name': 'Todo', 'empresa_id': empresa.id}, headers=headers)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['name'] == 'Todo'
        assert 'cards' not in data
        column_id = data['id']

        # Get
        resp = client.get(f'/api/columns/{column_id}', headers=headers)
        assert resp.status_code == 200
        assert resp.get_json()['id'] == column_id

        # Update
        resp = client.put(f'/api/columns/{column_id}', json={'name': 'Doing', 'empresa_id': empresa.id}, headers=headers)
        assert resp.status_code == 200
        assert resp.get_json()['name'] == 'Doing'

        # List
        resp = client.get('/api/columns', headers=headers)
        assert resp.status_code == 200
        assert any(c['id'] == column_id for c in resp.get_json())

        # Delete
        resp = client.delete(f'/api/columns/{column_id}', headers=headers)
        assert resp.status_code == 204

        resp = client.get(f'/api/columns/{column_id}', headers=headers)
        assert resp.status_code == 404
