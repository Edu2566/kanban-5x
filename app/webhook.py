from flask import Blueprint, request, jsonify, session
from .models import db, Empresa, Usuario
import json

webhook_bp = Blueprint('webhook', __name__)


@webhook_bp.route('/webhook/chatwoot', methods=['POST'])
def chatwoot_webhook():
    """Handle Chatwoot webhook requests."""
    query_header = request.headers.get('query', '{}')
    try:
        data = json.loads(query_header)
    except json.JSONDecodeError:
        return jsonify({'success': False, 'error': 'Invalid query header'}), 400

    account_id = data.get('account_id')
    user_email = data.get('user_email')
    user_id = data.get('user_id')
    user_name = data.get('user_name')

    if not all([account_id, user_email, user_id, user_name]):
        return jsonify({'success': False, 'error': 'Missing data'}), 400

    empresa = Empresa.query.filter_by(account_id=account_id).first()
    if not empresa:
        empresa = Empresa(account_id=account_id, nome=f'Empresa {account_id}')
        db.session.add(empresa)
        db.session.commit()

    usuario = (
        Usuario.query.filter_by(user_id=user_id, empresa_id=empresa.id).first()
    )
    if not usuario:
        usuario = Usuario(
            user_id=user_id,
            user_email=user_email,
            user_name=user_name,
            role='user',
            empresa_id=empresa.id,
        )
        db.session.add(usuario)
        db.session.commit()

    session['empresa_id'] = empresa.id
    session['usuario_id'] = usuario.id

    return jsonify({'success': True})
