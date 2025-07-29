from flask import request, jsonify, current_app

from app.models import db, Panel, Usuario

from . import api_bp, require_superadmin_token
from app.sse import publish_event


def _serialize(panel: Panel):
    return {
        "id": panel.id,
        "name": panel.name,
        "empresa_id": panel.empresa_id,
        "usuario_ids": [u.id for u in panel.usuarios],
    }


@api_bp.route("/panels", methods=["GET"])
@require_superadmin_token
def list_panels():
    query = Panel.query
    empresa_id = request.args.get("empresa_id", type=int)
    if empresa_id:
        query = query.filter(Panel.empresa_id == empresa_id)
    panels = query.all()
    return jsonify([_serialize(p) for p in panels])


@api_bp.route("/panels/<int:panel_id>", methods=["GET"])
@require_superadmin_token
def get_panel(panel_id):
    panel = Panel.query.get_or_404(panel_id)
    return jsonify(_serialize(panel))


@api_bp.route("/panels", methods=["POST"])
@require_superadmin_token
def create_panel():
    data = request.get_json(force=True) or {}
    name = data.get("name")
    empresa_id = data.get("empresa_id")
    usuario_ids = data.get("usuario_ids", [])
    if not name or not empresa_id:
        return jsonify({"error": "Missing name or empresa_id"}), 400
    usuarios = (
        Usuario.query.filter(Usuario.id.in_(usuario_ids)).all() if usuario_ids else []
    )
    panel = Panel(name=name, empresa_id=empresa_id, usuarios=usuarios)
    db.session.add(panel)
    db.session.commit()
    publish_event(current_app, empresa_id, {
        'type': 'panel_created',
        'panel': _serialize(panel)
    })
    return jsonify(_serialize(panel)), 201


@api_bp.route("/panels/<int:panel_id>", methods=["PUT"])
@require_superadmin_token
def update_panel(panel_id):
    panel = Panel.query.get_or_404(panel_id)
    data = request.get_json(force=True) or {}
    name = data.get("name", panel.name)
    empresa_id = data.get("empresa_id", panel.empresa_id)
    usuario_ids = data.get("usuario_ids", [u.id for u in panel.usuarios])
    usuarios = (
        Usuario.query.filter(Usuario.id.in_(usuario_ids)).all() if usuario_ids else []
    )
    panel.name = name
    panel.empresa_id = empresa_id
    panel.usuarios = usuarios
    db.session.commit()
    publish_event(current_app, panel.empresa_id, {
        'type': 'panel_updated',
        'panel': _serialize(panel)
    })
    return jsonify(_serialize(panel))


@api_bp.route("/panels/<int:panel_id>", methods=["DELETE"])
@require_superadmin_token
def delete_panel(panel_id):
    panel = Panel.query.get_or_404(panel_id)
    empresa_id = panel.empresa_id
    db.session.delete(panel)
    db.session.commit()
    publish_event(current_app, empresa_id, {
        'type': 'panel_deleted',
        'panel_id': panel_id
    })
    return "", 204
