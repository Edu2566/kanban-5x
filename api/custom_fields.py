import json
from flask import request, jsonify, abort

from app.models import db, Empresa
from app.routes.superadmin import parse_custom_fields, CustomFieldError

from . import api_bp, require_superadmin_token


@api_bp.route('/custom_fields/<int:empresa_id>', methods=['GET'])
@require_superadmin_token
def list_custom_fields(empresa_id):
    empresa = Empresa.query.get_or_404(empresa_id)
    return jsonify(empresa.custom_fields)


@api_bp.route('/custom_fields/<int:empresa_id>', methods=['POST'])
@require_superadmin_token
def add_custom_field(empresa_id):
    empresa = Empresa.query.get_or_404(empresa_id)
    data = request.get_json(force=True) or {}
    try:
        new_list = parse_custom_fields(
            json.dumps(empresa.custom_fields + [data])
        )
    except CustomFieldError as exc:
        return jsonify({'error': str(exc)}), 400
    empresa.custom_fields = new_list
    db.session.commit()
    return jsonify(empresa.custom_fields), 201


@api_bp.route('/custom_fields/<int:empresa_id>/<int:index>', methods=['PUT'])
@require_superadmin_token
def update_custom_field(empresa_id, index):
    empresa = Empresa.query.get_or_404(empresa_id)
    if index < 0 or index >= len(empresa.custom_fields):
        abort(404)
    data = request.get_json(force=True) or {}
    fields = list(empresa.custom_fields)
    fields[index] = data
    try:
        fields = parse_custom_fields(json.dumps(fields))
    except CustomFieldError as exc:
        return jsonify({'error': str(exc)}), 400
    empresa.custom_fields = fields
    db.session.commit()
    return jsonify(empresa.custom_fields)


@api_bp.route('/custom_fields/<int:empresa_id>/<int:index>', methods=['DELETE'])
@require_superadmin_token
def delete_custom_field(empresa_id, index):
    empresa = Empresa.query.get_or_404(empresa_id)
    if index < 0 or index >= len(empresa.custom_fields):
        abort(404)
    fields = list(empresa.custom_fields)
    fields.pop(index)
    empresa.custom_fields = fields
    db.session.commit()
    return '', 204

