import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Empresa, Usuario, Panel
from app.routes.superadmin import add_user_to_panels


def setup_app():
    os.environ['SUPERADMIN_TOKEN'] = 'token'
    return create_app()


def setup_users():
    e1 = Empresa(nome='E1', account_id='1')
    e2 = Empresa(nome='E2', account_id='2')
    db.session.add_all([e1, e2])
    db.session.commit()
    sa1 = Usuario(user_id='sa1', user_email='sa1@example.com', user_name='SA1', role='superadmin', empresa_id=e1.id)
    sa2 = Usuario(user_id='sa2', user_email='sa2@example.com', user_name='SA2', role='superadmin', empresa_id=e2.id)
    gestor = Usuario(user_id='g1', user_email='g1@example.com', user_name='G1', role='gestor', empresa_id=e1.id)
    regular = Usuario(user_id='u1', user_email='u1@example.com', user_name='U1', role='user', empresa_id=e1.id)
    db.session.add_all([sa1, sa2, gestor, regular])
    db.session.commit()
    return e1, sa1, sa2, gestor, regular


def test_panel_has_superadmins_and_gestor():
    app = setup_app()
    with app.app_context():
        empresa, sa1, sa2, gestor, regular = setup_users()
        client = app.test_client()
        headers = {'Authorization': 'Bearer token'}

        resp = client.post('/api/panels', json={'name': 'P', 'empresa_id': empresa.id}, headers=headers)
        assert resp.status_code == 201
        panel_id = resp.get_json()['id']
        panel = Panel.query.get(panel_id)
        ids = {u.id for u in panel.usuarios}
        assert {sa1.id, sa2.id, gestor.id} <= ids
        assert regular.id not in ids


def test_new_gestor_added_to_existing_panels():
    app = setup_app()
    with app.app_context():
        empresa = Empresa(nome='ACME', account_id='10')
        db.session.add(empresa)
        db.session.commit()
        client = app.test_client()
        headers = {'Authorization': 'Bearer token'}
        p1 = client.post('/api/panels', json={'name': 'A', 'empresa_id': empresa.id}, headers=headers)
        p2 = client.post('/api/panels', json={'name': 'B', 'empresa_id': empresa.id}, headers=headers)
        ids = [p1.get_json()['id'], p2.get_json()['id']]
        gestor = Usuario(user_id='g2', user_email='g2@example.com', user_name='G2', role='gestor', empresa_id=empresa.id)
        db.session.add(gestor)
        db.session.commit()
        add_user_to_panels(gestor)
        panels = [Panel.query.get(pid) for pid in ids]
        for panel in panels:
            assert gestor in panel.usuarios

