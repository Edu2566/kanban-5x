import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.routes.superadmin import parse_custom_fields, CustomFieldError


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

