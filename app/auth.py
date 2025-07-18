from functools import wraps
from flask import Blueprint, session, g, redirect, url_for, render_template

from .models import Usuario


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login')
def login_page():
    """Simple page shown when login is required."""
    return render_template('login.html')


def login_user(usuario: Usuario) -> None:
    """Persist logged in user info in the session."""
    session['usuario_id'] = usuario.id
    session['empresa_id'] = usuario.empresa_id
    g.user = usuario


def logout_user() -> None:
    """Clear session information."""
    session.clear()
    g.user = None


@auth_bp.before_app_request
def load_logged_in_user():
    """Load user from the session and store in ``g.user``."""
    user_id = session.get('usuario_id')
    if user_id is None:
        g.user = None
    else:
        g.user = Usuario.query.get(user_id)


@auth_bp.route('/logout')
def logout():
    """Simple logout route."""
    logout_user()
    return redirect(url_for('main.index'))


def login_required(view):
    """Ensure the user is logged in."""

    @wraps(view)
    def wrapped_view(**kwargs):
        if g.get('user') is None:
            return redirect(url_for('auth.login_page'))
        return view(**kwargs)

    return wrapped_view


def gestor_required(view):
    """Allow access only for gestores."""

    @wraps(view)
    def wrapped_view(**kwargs):
        if g.get('user') is None:
            return redirect(url_for('auth.login_page'))
        if g.user.role != 'gestor':
            return 'Acesso restrito aos gestores', 403
        return view(**kwargs)

    return wrapped_view

