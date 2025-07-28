from flask import Blueprint, render_template, request, redirect, url_for, session, abort, g

from ..models import db, Panel, Empresa, Usuario
from .superadmin import _require_token, redirect_next

panels_bp = Blueprint('panels', __name__, url_prefix='/superadmin')


@panels_bp.before_request
def check_superadmin_token():
    if g.get('user') and g.user.role == 'superadmin':
        return
    _require_token()


@panels_bp.route('/create_panel', methods=['GET', 'POST'])
def create_panel():
    empresas = Empresa.query.all()
    usuarios = Usuario.query.filter(Usuario.role != 'superadmin').all()
    if request.method == 'POST':
        name = request.form['name']
        empresa_id = int(request.form['empresa_id'])
        user_ids = [int(uid) for uid in request.form.getlist('usuario_ids')]
        panel = Panel(name=name, empresa_id=empresa_id)
        if user_ids:
            panel.usuarios = Usuario.query.filter(Usuario.id.in_(user_ids)).all()
        db.session.add(panel)
        db.session.commit()
        return redirect_next('superadmin.dashboard')
    empresa_id = request.args.get('empresa_id', type=int)
    return render_template(
        'superadmin/create_panel.html',
        empresas=empresas,
        usuarios=usuarios,
        empresa_id=empresa_id,
    )


@panels_bp.route('/edit_panel/<int:panel_id>', methods=['GET', 'POST'])
def edit_panel(panel_id):
    panel = Panel.query.get_or_404(panel_id)
    empresas = Empresa.query.all()
    usuarios = Usuario.query.filter(Usuario.role != 'superadmin').all()
    if request.method == 'POST':
        panel.name = request.form['name']
        panel.empresa_id = int(request.form['empresa_id'])
        user_ids = [int(uid) for uid in request.form.getlist('usuario_ids')]
        panel.usuarios = Usuario.query.filter(Usuario.id.in_(user_ids)).all()
        db.session.commit()
        return redirect_next('superadmin.dashboard')
    return render_template(
        'superadmin/edit_panel.html',
        panel=panel,
        empresas=empresas,
        usuarios=usuarios,
    )


@panels_bp.route('/delete_panel/<int:panel_id>', methods=['POST'])
def delete_panel(panel_id):
    panel = Panel.query.get_or_404(panel_id)
    db.session.delete(panel)
    db.session.commit()
    return redirect_next('superadmin.dashboard')
