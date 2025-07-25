import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Empresa


def setup_app():
    os.environ['SUPERADMIN_TOKEN'] = 'token'
    return create_app()


def create_empresa():
    empresa = Empresa(nome='ACME', account_id='1')
    db.session.add(empresa)
    db.session.commit()
    return empresa


def test_custom_fields_crud():
    app = setup_app()
    with app.app_context():
        empresa = create_empresa()
        client = app.test_client()
        headers = {'SUPERADMIN_TOKEN': 'token'}

        # Initially empty
        resp = client.get(f'/api/custom_fields/{empresa.id}', headers=headers)
        assert resp.status_code == 200
        assert resp.get_json() == []

        # Create
        field = {'name': 'Status', 'type': 'select', 'options': ['Novo']}
        resp = client.post(f'/api/custom_fields/{empresa.id}', json=field, headers=headers)
        assert resp.status_code == 201
        assert resp.get_json()[0]['name'] == 'Status'

        # Update
        new_field = {'name': 'Obs', 'type': 'text'}
        resp = client.put(f'/api/custom_fields/{empresa.id}/0', json=new_field, headers=headers)
        assert resp.status_code == 200
        assert resp.get_json()[0]['name'] == 'Obs'

        # Delete
        resp = client.delete(f'/api/custom_fields/{empresa.id}/0', headers=headers)
        assert resp.status_code == 204
        resp = client.get(f'/api/custom_fields/{empresa.id}', headers=headers)
        assert resp.get_json() == []


def test_custom_fields_validation():
    app = setup_app()
    with app.app_context():
        empresa = create_empresa()
        client = app.test_client()
        headers = {'SUPERADMIN_TOKEN': 'token'}

        invalid_field = {'name': 'x'}  # Missing type
        resp = client.post(f'/api/custom_fields/{empresa.id}', json=invalid_field, headers=headers)
        assert resp.status_code == 400

        # Create 8 valid fields
        field = {'name': 'F', 'type': 'text'}
        for i in range(8):
            resp = client.post(f'/api/custom_fields/{empresa.id}', json={'name': f'f{i}', 'type': 'text'}, headers=headers)
            assert resp.status_code == 201
        # Attempt to add ninth
        resp = client.post(f'/api/custom_fields/{empresa.id}', json=field, headers=headers)
        assert resp.status_code == 400

