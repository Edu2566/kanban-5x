from flask import request, jsonify, abort

from app.models import db, Card, Column, Panel, Usuario
from app.routes.main import MAX_VALOR_NEGOCIADO

from . import api_bp, require_superadmin_token


def _build_custom_data(json_data, empresa):
    """Construct custom_data dict from JSON payload based on empresa fields."""
    result = {}
    for field in empresa.custom_fields:
        name = field.get("name")
        ftype = field.get("type")
        val = json_data.get(name)
        if ftype == "number":
            try:
                val = float(val) if val is not None else None
            except (TypeError, ValueError):
                val = None
        elif ftype == "boolean":
            val = bool(val)
        # text and select just use raw value
        result[name] = val
    return result


def _serialize(card: Card):
    return {
        "id": card.id,
        "title": card.title,
        "valor_negociado": card.valor_negociado,
        "conversa": card.conversa,
        "conversation_id": card.conversation_id,
        "column_id": card.column_id,
        "panel_id": card.column.panel_id if card.column else None,
        "vendedor_id": card.vendedor_id,
        "custom_data": card.custom_data,
    }


@api_bp.route("/cards", methods=["GET"])
@require_superadmin_token
def list_cards():
    query = Card.query
    empresa_id = request.args.get("empresa_id", type=int)
    panel_id = request.args.get("panel_id", type=int)
    column_id = request.args.get("column_id", type=int)
    conversation_id = request.args.get("conversation_id")
    if empresa_id or panel_id:
        query = query.join(Column).join(Panel)
    if empresa_id:
        query = query.filter(Panel.empresa_id == empresa_id)
    if panel_id:
        query = query.filter(Column.panel_id == panel_id)
    if column_id:
        query = query.filter(Card.column_id == column_id)
    if conversation_id:
        query = query.filter(Card.conversation_id == conversation_id)
    cards = query.all()
    return jsonify([_serialize(c) for c in cards])


@api_bp.route("/cards/<int:card_id>", methods=["GET"])
@require_superadmin_token
def get_card(card_id):
    card = Card.query.get_or_404(card_id)
    return jsonify(_serialize(card))


@api_bp.route("/cards/by_conversation/<string:conversation_id>", methods=["GET"])
@require_superadmin_token
def get_card_by_conversation(conversation_id):
    card = Card.query.filter_by(conversation_id=conversation_id).first()
    if not card:
        abort(404)
    return jsonify(_serialize(card))


@api_bp.route("/cards", methods=["POST"])
@require_superadmin_token
def create_card():
    data = request.get_json(force=True) or {}
    title = data.get("title")
    column_id = data.get("column_id")
    if title is None or column_id is None:
        return jsonify({"error": "Missing title or column_id"}), 400
    valor_negociado = data.get("valor_negociado")
    if valor_negociado is not None and valor_negociado > MAX_VALOR_NEGOCIADO:
        return jsonify({"error": "valor_negociado acima do limite"}), 400
    conversa = data.get("conversa")
    conversation_id = data.get("conversation_id")
    vendedor_id = data.get("vendedor_id")

    column = Column.query.get_or_404(column_id)
    panel = column.panel
    if panel and vendedor_id is not None:
        allowed = {u.id for u in panel.usuarios}
        if vendedor_id not in allowed:
            return jsonify({"error": "vendedor_id nao pertence ao painel"}), 400
    custom_data = _build_custom_data(data, column.empresa)

    card = Card(
        title=title,
        valor_negociado=valor_negociado,
        conversa=conversa,
        conversation_id=conversation_id,
        column_id=column_id,
        vendedor_id=vendedor_id,
        custom_data=custom_data,
    )
    db.session.add(card)
    db.session.commit()
    return jsonify(_serialize(card)), 201


@api_bp.route("/cards/<int:card_id>", methods=["PUT"])
@require_superadmin_token
def update_card(card_id):
    card = Card.query.get_or_404(card_id)
    data = request.get_json(force=True) or {}

    title = data.get("title", card.title)
    valor_negociado = data.get("valor_negociado", card.valor_negociado)
    if valor_negociado is not None and valor_negociado > MAX_VALOR_NEGOCIADO:
        return jsonify({"error": "valor_negociado acima do limite"}), 400
    conversa = data.get("conversa", card.conversa)
    conversation_id = data.get("conversation_id", card.conversation_id)
    column_id = data.get("column_id", card.column_id)
    vendedor_id = data.get("vendedor_id", card.vendedor_id)

    column = Column.query.get_or_404(column_id)
    panel = column.panel
    if panel and vendedor_id is not None:
        allowed = {u.id for u in panel.usuarios}
        if vendedor_id not in allowed:
            return jsonify({"error": "vendedor_id nao pertence ao painel"}), 400
    custom_data = _build_custom_data(data, column.empresa)

    card.title = title
    card.valor_negociado = valor_negociado
    card.conversa = conversa
    card.conversation_id = conversation_id
    card.column_id = column_id
    card.vendedor_id = vendedor_id
    card.custom_data = custom_data
    db.session.commit()
    return jsonify(_serialize(card))


@api_bp.route("/cards/<int:card_id>", methods=["DELETE"])
@require_superadmin_token
def delete_card(card_id):
    card = Card.query.get_or_404(card_id)
    db.session.delete(card)
    db.session.commit()
    return "", 204
