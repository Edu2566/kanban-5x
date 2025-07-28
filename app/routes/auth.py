from functools import wraps
from flask import Blueprint, session, g, redirect, url_for, render_template

from ..models import Usuario


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login')
def login_page():
    """Simple page shown when login is required."""
    return render_template('login.html')


def login_user(usuario: Usuario) -> None:
    """Persist logged in user info in the session."""
    session['vendedor_id'] = usuario.id
    session['empresa_id'] = usuario.empresa_id
    g.user = usuario


def logout_user() -> None:
    """Clear session information."""
    session.clear()
    g.user = None


@auth_bp.before_app_request
def load_logged_in_user():
    """Load user from the session and store in ``g.user``."""
    user_id = session.get('vendedor_id')
    if user_id is None:
        g.user = None
    else:
        g.user = Usuario.query.get(user_id)


@auth_bp.route('/logout')
def logout():
    """Simple logout route."""
    logout_user()
    return redirect(url_for('main.index'))


def role_required(*roles):
    """Ensure the logged user has one of the given roles."""

    def decorator(view):
        @wraps(view)
        def wrapped_view(**kwargs):
            if g.get('user') is None:
                return redirect(url_for('auth.login_page'))
            if roles and g.user.role not in roles:
                return "Acesso negado", 403
            return view(**kwargs)

        return wrapped_view

    return decorator


def login_required(view):
    """Ensure the user is logged in."""

    return role_required()(view)

def superadmin_required(view):
    """Allow access only for super-admins."""

    return role_required('superadmin')(view)


def gestor_required(view):
    """Allow access only for gestores."""

    return role_required('gestor')(view)


def is_panel_member(panel) -> bool:
    """Return ``True`` if ``g.user`` is member of the given panel."""

    if panel is None:
        return False
    return any(u.id == g.user.id for u in panel.usuarios)


def has_panel_access(panel) -> bool:
    """Check whether ``g.user`` may access ``panel``."""

    if g.get('user') is None:
        return False
    if g.user.role == 'superadmin':
        return True
    if panel is None:
        return False
    if panel.empresa_id != g.user.empresa_id:
        return False
    if g.user.role == 'gestor':
        return True
    return is_panel_member(panel)

