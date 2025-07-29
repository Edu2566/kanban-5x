import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from flask import g

from app import create_app, db
from app.models import Empresa, Usuario, Column, Panel
from app.routes.main import MAX_VALOR_NEGOCIADO


def setup_basic_data():
    """Create a minimal Empresa, Usuario and Column for tests."""
    empresa = Empresa(nome="ACME", account_id="1")
    db.session.add(empresa)
    db.session.commit()
    usuario = Usuario(
        user_id="1",
        user_email="u@example.com",
        user_name="U",
        role="gestor",
        empresa_id=empresa.id,
    )
    panel = Panel(name="Main", empresa_id=empresa.id)
    column = Column(name="Todo", panel_id=panel.id)
    db.session.add_all([usuario, panel, column])
    db.session.commit()
    return usuario, column


def test_valor_negociado_limit_exceeded():
    app = create_app()
    with app.app_context():
        user, column = setup_basic_data()
        g.user = user
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['vendedor_id'] = user.id
            sess['empresa_id'] = user.empresa_id
        resp = client.post(
            f'/add_card/{column.id}',
            data={'title': 'x', 'valor_negociado': MAX_VALOR_NEGOCIADO + 1}
        )
        assert resp.status_code == 400

