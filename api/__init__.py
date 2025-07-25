import os
from functools import wraps
from flask import Blueprint, request, abort, jsonify


api_bp = Blueprint('api', __name__, url_prefix='/api')


def require_superadmin_token(view):
    """Ensure request contains correct SUPERADMIN_TOKEN header."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        required = os.environ.get('SUPERADMIN_TOKEN')
        token = request.headers.get('SUPERADMIN_TOKEN')
        if not required or token != required:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


@api_bp.route('/ping')
@require_superadmin_token
def ping():
    """Simple authenticated ping endpoint."""
    return jsonify({'message': 'pong'})
