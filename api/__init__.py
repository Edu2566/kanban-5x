import os
from functools import wraps
from flask import Blueprint, request, abort, jsonify


api_bp = Blueprint('api', __name__, url_prefix='/api')


def require_superadmin_token(view):
    """Ensure request contains correct SUPERADMIN_TOKEN via Authorization Bearer."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        required = os.environ.get('SUPERADMIN_TOKEN')
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.removeprefix('Bearer ').strip() if auth_header.startswith('Bearer ') else None
        if not required or token != required:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


@api_bp.route('/ping')
@require_superadmin_token
def ping():
    """Simple authenticated ping endpoint."""
    return jsonify({'message': 'pong'})


# Import additional API endpoints
from . import cards  # noqa: E402,F401
from . import columns  # noqa: E402,F401
from . import custom_fields  # noqa: E402,F401
from . import panels  # noqa: E402,F401
