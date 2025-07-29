from flask import request, jsonify, abort

from app.models import db, Column, Panel

from . import api_bp, require_superadmin_token


def _serialize(column: Column):
    return {
        "id": column.id,
        "name": column.name,
        "empresa_id": column.empresa_id,
        "color": column.color,
        "panel_id": column.panel_id,
    }


@api_bp.route("/columns", methods=["GET"])
@require_superadmin_token
def list_columns():
    query = Column.query
    empresa_id = request.args.get("empresa_id", type=int)
    panel_id = request.args.get("panel_id", type=int)
    if empresa_id:
        query = query.filter(Column.empresa_id == empresa_id)
    if panel_id is not None:
        query = query.filter(Column.panel_id == panel_id)
    columns = query.all()
    return jsonify([_serialize(c) for c in columns])


@api_bp.route("/columns/<int:column_id>", methods=["GET"])
@require_superadmin_token
def get_column(column_id):
    column = Column.query.get_or_404(column_id)
    return jsonify(_serialize(column))


@api_bp.route("/columns", methods=["POST"])
@require_superadmin_token
def create_column():
    data = request.get_json(force=True) or {}
    name = data.get("name")
    panel_id = data.get("panel_id")
    empresa_id = data.get("empresa_id")
    color = data.get("color")
    if not name or panel_id is None:
        return jsonify({"error": "Missing name or panel_id"}), 400
    panel = Panel.query.get_or_404(panel_id)
    if empresa_id is None:
        empresa_id = panel.empresa_id
    elif panel.empresa_id != empresa_id:
        return jsonify({"error": "panel_id nao pertence a empresa"}), 400
    column = Column(name=name, empresa_id=empresa_id, color=color, panel_id=panel_id)
    db.session.add(column)
    db.session.commit()
    return jsonify(_serialize(column)), 201


@api_bp.route("/columns/<int:column_id>", methods=["PUT"])
@require_superadmin_token
def update_column(column_id):
    column = Column.query.get_or_404(column_id)
    data = request.get_json(force=True) or {}
    name = data.get("name", column.name)
    panel_id = data.get("panel_id", column.panel_id)
    empresa_id = data.get("empresa_id")
    color = data.get("color", column.color)
    if panel_id is None:
        return jsonify({"error": "Missing panel_id"}), 400
    panel = Panel.query.get_or_404(panel_id)
    if empresa_id is None:
        empresa_id = panel.empresa_id
    elif panel.empresa_id != empresa_id:
        return jsonify({"error": "panel_id nao pertence a empresa"}), 400
    column.name = name
    column.empresa_id = empresa_id
    column.panel_id = panel_id
    column.color = color
    db.session.commit()
    return jsonify(_serialize(column))


@api_bp.route("/columns/<int:column_id>", methods=["DELETE"])
@require_superadmin_token
def delete_column(column_id):
    column = Column.query.get_or_404(column_id)
    db.session.delete(column)
    db.session.commit()
    return "", 204
