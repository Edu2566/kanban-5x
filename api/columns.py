from flask import request, jsonify, abort

from app.models import db, Column

from . import api_bp, require_superadmin_token


def _serialize(column: Column):
    return {
        "id": column.id,
        "name": column.name,
        "empresa_id": column.empresa_id,
    }


@api_bp.route("/columns", methods=["GET"])
@require_superadmin_token
def list_columns():
    query = Column.query
    empresa_id = request.args.get("empresa_id", type=int)
    if empresa_id:
        query = query.filter(Column.empresa_id == empresa_id)
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
    empresa_id = data.get("empresa_id")
    if not name or not empresa_id:
        return jsonify({"error": "Missing name or empresa_id"}), 400
    column = Column(name=name, empresa_id=empresa_id)
    db.session.add(column)
    db.session.commit()
    return jsonify(_serialize(column)), 201


@api_bp.route("/columns/<int:column_id>", methods=["PUT"])
@require_superadmin_token
def update_column(column_id):
    column = Column.query.get_or_404(column_id)
    data = request.get_json(force=True) or {}
    name = data.get("name", column.name)
    empresa_id = data.get("empresa_id", column.empresa_id)
    column.name = name
    column.empresa_id = empresa_id
    db.session.commit()
    return jsonify(_serialize(column))


@api_bp.route("/columns/<int:column_id>", methods=["DELETE"])
@require_superadmin_token
def delete_column(column_id):
    column = Column.query.get_or_404(column_id)
    db.session.delete(column)
    db.session.commit()
    return "", 204
