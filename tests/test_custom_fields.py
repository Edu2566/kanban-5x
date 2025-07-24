import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.routes.superadmin import parse_custom_fields, CustomFieldError
from app.routes.main import build_custom_data
from app import create_app
from flask import g
from types import SimpleNamespace


def test_parse_valid_definition():
    raw = '[{"name": "Status", "type": "select", "options": ["Novo"]}, {"name": "Obs", "type": "text"}]'
    result = parse_custom_fields(raw)
    assert result == [
        {"name": "Status", "type": "select", "options": ["Novo"]},
        {"name": "Obs", "type": "text"},
    ]


@pytest.mark.parametrize("raw", [
    'not json',
    '{}',
    '[{"type": "text"}]',
    '[{"name": "x"}]',
    '[{"name": "x", "type": "select"}]',
    '[{"name": "x", "type": "select", "options": []}]',
])
def test_parse_invalid_definition(raw):
    with pytest.raises(CustomFieldError):
        parse_custom_fields(raw)


def test_build_custom_data_boolean_and_select():
    app = create_app()
    with app.app_context():
        g.user = SimpleNamespace(
            empresa=SimpleNamespace(
                custom_fields=[
                    {"name": "Ativo", "type": "boolean"},
                    {"name": "Status", "type": "select", "options": ["A", "B"]},
                ]
            )
        )
        form = {"custom_Ativo": "on", "custom_Status": "B"}
        data = build_custom_data(form)
        assert data == {"Ativo": True, "Status": "B"}


def test_build_custom_data_boolean_missing():
    app = create_app()
    with app.app_context():
        g.user = SimpleNamespace(
            empresa=SimpleNamespace(custom_fields=[{"name": "Flag", "type": "boolean"}])
        )
        form = {}
        data = build_custom_data(form)
        assert data == {"Flag": False}

