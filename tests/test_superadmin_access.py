import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Empresa, Panel, Usuario


def setup_app():
    os.environ['SUPERADMIN_TOKEN'] = 'token'
    return create_app()


def setup_data():
    e1 = Empresa(nome='E1', account_id='1')
    e2 = Empresa(nome='E2', account_id='2')
    db.session.add_all([e1, e2])
    db.session.commit()
    p1 = Panel(name='P1', empresa_id=e1.id)
    p2 = Panel(name='P2', empresa_id=e2.id)
    sa = Usuario(user_id='sa', user_email='sa@example.com', user_name='SA', role='superadmin', empresa_id=e1.id)
    db.session.add_all([p1, p2, sa])
    db.session.commit()
    return e1, e2, p1, p2, sa


def test_superadmin_lists_all_panels():
    app = setup_app()
    with app.app_context():
        e1, e2, p1, p2, sa = setup_data()
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['vendedor_id'] = sa.id
            sess['empresa_id'] = sa.empresa_id
        resp = client.get('/')
        text = resp.get_data(as_text=True)
        assert resp.status_code == 200
        assert p1.name in text
        assert p2.name in text


def test_superadmin_switch_empresa_via_query():
    app = setup_app()
    with app.app_context():
        e1, e2, p1, p2, sa = setup_data()
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['vendedor_id'] = sa.id
            sess['empresa_id'] = sa.empresa_id
        resp = client.get(f'/?empresa_id={e2.id}')
        assert resp.status_code == 200
        text = resp.get_data(as_text=True)
        assert p2.name in text
        assert p1.name not in text
        with client.session_transaction() as sess:
            assert sess['empresa_id'] == e2.id


def test_superadmin_select_panel_updates_empresa():
    app = setup_app()
    with app.app_context():
        e1, e2, p1, p2, sa = setup_data()
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['vendedor_id'] = sa.id
            sess['empresa_id'] = e1.id
        resp = client.post('/select_panel', data={'panel_id': p2.id})
        assert resp.status_code == 302
        with client.session_transaction() as sess:
            assert sess['panel_id'] == p2.id
            assert sess['empresa_id'] == e2.id
