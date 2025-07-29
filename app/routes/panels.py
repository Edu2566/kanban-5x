from flask import Blueprint, render_template, request, redirect, url_for, session, abort, g, current_app

from ..models import db, Panel, Empresa, Usuario, Column
from .superadmin import _require_token, redirect_next
from ..sse import publish_event
from api.panels import _serialize as serialize_panel
from api.columns import _serialize as serialize_column

panels_bp = Blueprint('panels', __name__, url_prefix='/superadmin')


@panels_bp.before_request
def check_superadmin_token():
    if g.get('user') and g.user.role == 'superadmin':
        return
    _require_token()


@panels_bp.route('/create_panel', methods=['GET', 'POST'])
def create_panel():
    empresas = Empresa.query.all()
    if request.method == 'POST':
        name = request.form['name']
        empresa_id = int(request.form['empresa_id'])
        user_ids = [int(uid) for uid in request.form.getlist('usuario_ids')]
        panel = Panel(name=name, empresa_id=empresa_id)
        if user_ids:
            panel.usuarios = Usuario.query.filter(Usuario.id.in_(user_ids)).all()
        db.session.add(panel)
        db.session.commit()
        publish_event(current_app, empresa_id, {
            'type': 'panel_created',
            'panel': serialize_panel(panel)
        })
        return redirect_next('superadmin.dashboard')

    empresa_id = request.args.get('empresa_id', type=int)
    if not empresa_id and empresas:
        empresa_id = empresas[0].id

    usuarios = []
    if empresa_id:
        usuarios = (
            Usuario.query.filter(
                Usuario.role != 'superadmin', Usuario.empresa_id == empresa_id
            ).all()
        )
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
    if request.method == 'POST':
        panel.name = request.form['name']
        panel.empresa_id = int(request.form['empresa_id'])
        user_ids = [int(uid) for uid in request.form.getlist('usuario_ids')]
        panel.usuarios = Usuario.query.filter(Usuario.id.in_(user_ids)).all()
        db.session.commit()
        publish_event(current_app, panel.empresa_id, {
            'type': 'panel_updated',
            'panel': serialize_panel(panel)
        })
        return redirect_next('superadmin.dashboard')

    usuarios = (
        Usuario.query.filter(
            Usuario.role != 'superadmin', Usuario.empresa_id == panel.empresa_id
        ).all()
    )
    return render_template(
        'superadmin/edit_panel.html',
        panel=panel,
        empresas=empresas,
        usuarios=usuarios,
    )


@panels_bp.route('/delete_panel/<int:panel_id>', methods=['POST'])
def delete_panel(panel_id):
    panel = Panel.query.get_or_404(panel_id)
    empresa_id = panel.empresa_id
    db.session.delete(panel)
    db.session.commit()
    publish_event(current_app, empresa_id, {
        'type': 'panel_deleted',
        'panel_id': panel_id
    })
    return redirect_next('superadmin.dashboard')


# Column management -------------------------------------------------------

@panels_bp.route('/create_column/<int:panel_id>', methods=['GET', 'POST'])
def create_column(panel_id):
    panel = Panel.query.get_or_404(panel_id)
    if request.method == 'POST':
        name = request.form['name']
        color = request.form.get('color')
        column = Column(
            name=name,
            color=color,
            panel_id=panel.id,
        )
        db.session.add(column)
        db.session.commit()
        publish_event(current_app, panel.empresa_id, {
            'type': 'column_created',
            'column': serialize_column(column)
        })
        next_url = request.form.get('next') or request.args.get('next')
        if next_url:
            return redirect(next_url)
        return redirect(
            url_for(
                'panels.edit_panel',
                panel_id=panel.id,
                token=session.get('superadmin_token'),
            )
        )
    return render_template('superadmin/create_column.html', panel=panel)


@panels_bp.route('/edit_column/<int:column_id>', methods=['GET', 'POST'])
def edit_column(column_id):
    column = Column.query.get_or_404(column_id)
    panels = Panel.query.all()
    if request.method == 'POST':
        column.name = request.form['name']
        column.color = request.form.get('color')
        panel_id = int(request.form['panel_id'])
        panel = Panel.query.get_or_404(panel_id)
        column.panel_id = panel_id
        db.session.commit()
        publish_event(current_app, column.panel.empresa_id, {
            'type': 'column_updated',
            'column': serialize_column(column)
        })
        next_url = request.form.get('next') or request.args.get('next')
        if next_url:
            return redirect(next_url)
        return redirect(
            url_for(
                'panels.edit_panel',
                panel_id=panel_id,
                token=session.get('superadmin_token'),
            )
        )
    return render_template('superadmin/edit_column.html', column=column, panels=panels)


@panels_bp.route('/delete_column/<int:column_id>', methods=['POST'])
def delete_column(column_id):
    column = Column.query.get_or_404(column_id)
    panel_id = column.panel_id
    empresa_id = column.panel.empresa_id
    db.session.delete(column)
    db.session.commit()
    publish_event(current_app, empresa_id, {
        'type': 'column_deleted',
        'column_id': column_id
    })
    next_url = request.form.get('next') or request.args.get('next')
    if next_url:
        return redirect(next_url)
    return redirect(
        url_for(
            'panels.edit_panel',
            panel_id=panel_id,
            token=session.get('superadmin_token'),
        )
    )
