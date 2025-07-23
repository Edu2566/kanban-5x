from flask import Blueprint, request, jsonify, redirect, url_for
from ..models import db, Empresa, Usuario
from .auth import login_user
import json

webhook_bp = Blueprint("webhook", __name__)


@webhook_bp.route("/webhook/chatwoot", methods=["POST", "GET"])
def chatwoot_webhook():
    """Handle Chatwoot webhook requests."""
    if request.method == "POST":
        # Espera payload JSON no body do webhook
        try:
            data = request.get_json(force=True) or {}
        except Exception:
            return jsonify({"success": False, "error": "Invalid JSON body"}), 400
    else:
        # Suporte para teste via GET com parâmetros na query string
        data = request.args.to_dict()

    # Extrai informações do webhook (ajuste conforme payload do Chatwoot)
    account_id = data.get("account_id")
    user_email = data.get("user_email") or data.get("email")
    user_id = data.get("user_id") or str(data.get("id", ""))
    user_name = data.get("user_name") or data.get("name")

    if not all([account_id, user_email, user_id, user_name]):
        return jsonify({"success": False, "error": "Missing data"}), 400

    empresa = Empresa.query.filter_by(account_id=account_id).first()
    if not empresa:
        empresa = Empresa(account_id=account_id, nome=f"Empresa {account_id}")
        db.session.add(empresa)
        db.session.commit()

    usuario = Usuario.query.filter_by(user_id=user_id, empresa_id=empresa.id).first()
    if not usuario:
        usuario = Usuario(
            user_id=user_id,
            user_email=user_email,
            user_name=user_name,
            role="user",
            empresa_id=empresa.id,
        )
        db.session.add(usuario)
        db.session.commit()

    login_user(usuario)

    return redirect(url_for('main.index'))
