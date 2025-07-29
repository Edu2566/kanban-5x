import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Empresa, Panel, Column, Usuario, Card


def setup_app():
    return create_app()


def setup_cross_empresa():
    e1 = Empresa(nome='E1', account_id='1')
    e2 = Empresa(nome='E2', account_id='2')
    db.session.add_all([e1, e2])
    db.session.commit()
    p1 = Panel(name='P1', empresa_id=e1.id)
    c1 = Column(name='Todo1', panel_id=p1.id)
    p2 = Panel(name='P2', empresa_id=e2.id)
    c2 = Column(name='Todo2', panel_id=p2.id)
    u1 = Usuario(user_id='1', user_email='u1@example.com', user_name='U1', role='gestor', empresa_id=e1.id)
    p1.usuarios.append(u1)
    db.session.add_all([p1, c1, p2, c2, u1])
    db.session.commit()
    return u1, c1, c2, p2


def setup_no_access():
    empresa = Empresa(nome='ACME', account_id='3')
    db.session.add(empresa)
    db.session.commit()
    panel = Panel(name='NoAccess', empresa_id=empresa.id)
    column = Column(name='Todo', panel_id=panel.id)
    user = Usuario(user_id='2', user_email='u2@example.com', user_name='U2', role='user', empresa_id=empresa.id)
    db.session.add_all([panel, column, user])
    db.session.commit()
    return user, column, panel


def login(client, user):
    with client.session_transaction() as sess:
        sess['vendedor_id'] = user.id
        sess['empresa_id'] = user.empresa_id


def test_add_card_wrong_empresa():
    app = setup_app()
    with app.app_context():
        user, c1, c2, panel2 = setup_cross_empresa()
        client = app.test_client()
        login(client, user)
        resp = client.post(f'/add_card/{c2.id}', data={'title': 'x'})
        assert resp.status_code == 404


def test_add_card_without_panel_access():
    app = setup_app()
    with app.app_context():
        user, column, panel = setup_no_access()
        client = app.test_client()
        login(client, user)
        resp = client.post(f'/add_card/{column.id}', data={'title': 'x'})
        assert resp.status_code == 403


def test_add_column_wrong_empresa():
    app = setup_app()
    with app.app_context():
        user, c1, c2, panel2 = setup_cross_empresa()
        client = app.test_client()
        login(client, user)
        resp = client.post('/add_column', data={'name': 'X', 'panel_id': panel2.id})
        assert resp.status_code == 404


def test_add_column_without_panel_access():
    app = setup_app()
    with app.app_context():
        user, column, panel = setup_no_access()
        client = app.test_client()
        login(client, user)
        resp = client.post('/add_column', data={'name': 'X', 'panel_id': panel.id})
        assert resp.status_code == 403

