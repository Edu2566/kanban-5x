import os
from flask import Blueprint, render_template, request, redirect, url_for, session, abort, g
import json
from .models import db, Empresa, Usuario, Column

superadmin_bp = Blueprint('superadmin', __name__, url_prefix='/superadmin')


def _require_token():
    required = os.environ.get('SUPERADMIN_TOKEN')
    token = request.args.get('token') or session.get('superadmin_token')
    if not required or token != required:
        abort(403)
    session['superadmin_token'] = token


@superadmin_bp.before_request
def check_superadmin_token():
    # Allow super-admin role to access without token
    if g.get('user') and g.user.role == 'superadmin':
        return
    _require_token()


@superadmin_bp.route('/')
def dashboard():
    empresas = Empresa.query.all()
    return render_template('superadmin/dashboard.html', empresas=empresas)


@superadmin_bp.route('/empresa/<int:empresa_id>')
def empresa_detail(empresa_id):
    empresa = Empresa.query.get_or_404(empresa_id)
    usuarios = Usuario.query.filter_by(empresa_id=empresa_id).all()
    columns = Column.query.filter_by(empresa_id=empresa_id).all()
    return render_template(
        'superadmin/empresa_detail.html',
        empresa=empresa,
        usuarios=usuarios,
        columns=columns,
    )


@superadmin_bp.route('/create_empresa', methods=['GET', 'POST'])
def create_empresa():
    if request.method == 'POST':
        nome = request.form['nome']
        account_id = request.form['account_id']
        # Campos customizáveis em JSON (até 8 definições)
        raw = request.form.get('custom_fields', '[]')
        try:
            cf = json.loads(raw)
        except json.JSONDecodeError:
            cf = []
        empresa = Empresa(nome=nome, account_id=account_id,
                          custom_fields=cf[:8])
        db.session.add(empresa)
        db.session.commit()
        next_url = request.form.get('next') or request.args.get('next')
        if next_url:
            return redirect(next_url)
        return redirect(url_for('superadmin.dashboard', token=session.get('superadmin_token')))
    return render_template('superadmin/create_empresa.html')


@superadmin_bp.route('/edit_empresa/<int:empresa_id>', methods=['GET', 'POST'])
def edit_empresa(empresa_id):
    empresa = Empresa.query.get_or_404(empresa_id)
    if request.method == 'POST':
        empresa.nome = request.form['nome']
        empresa.account_id = request.form['account_id']
        # Atualiza campos customizáveis JSON
        raw = request.form.get('custom_fields', '[]')
        try:
            cf = json.loads(raw)
        except json.JSONDecodeError:
            cf = []
        empresa.custom_fields = cf[:8]
        db.session.commit()
        next_url = request.form.get('next') or request.args.get('next')
        if next_url:
            return redirect(next_url)
        return redirect(url_for('superadmin.dashboard', token=session.get('superadmin_token')))
    return render_template('superadmin/edit_empresa.html', empresa=empresa)


@superadmin_bp.route('/delete_empresa/<int:empresa_id>', methods=['POST'])
def delete_empresa(empresa_id):
    empresa = Empresa.query.get_or_404(empresa_id)
    db.session.delete(empresa)
    db.session.commit()
    next_url = request.form.get('next') or request.args.get('next')
    if next_url:
        return redirect(next_url)
    return redirect(url_for('superadmin.dashboard', token=session.get('superadmin_token')))


@superadmin_bp.route('/create_usuario', methods=['GET', 'POST'])
def create_usuario():
    empresas = Empresa.query.all()
    if request.method == 'POST':
        usuario = Usuario(
            user_id=request.form['user_id'],
            user_email=request.form['user_email'],
            user_name=request.form['user_name'],
            role=request.form['role'],
            empresa_id=int(request.form['empresa_id']),
        )
        db.session.add(usuario)
        db.session.commit()
        next_url = request.form.get('next') or request.args.get('next')
        if next_url:
            return redirect(next_url)
        return redirect(url_for('superadmin.dashboard', token=session.get('superadmin_token')))
    return render_template('superadmin/create_usuario.html', empresas=empresas)


@superadmin_bp.route('/edit_usuario/<int:usuario_id>', methods=['GET', 'POST'])
def edit_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    empresas = Empresa.query.all()
    if request.method == 'POST':
        usuario.user_id = request.form['user_id']
        usuario.user_email = request.form['user_email']
        usuario.user_name = request.form['user_name']
        usuario.role = request.form['role']
        usuario.empresa_id = int(request.form['empresa_id'])
        db.session.commit()
        next_url = request.form.get('next') or request.args.get('next')
        if next_url:
            return redirect(next_url)
        return redirect(url_for('superadmin.dashboard', token=session.get('superadmin_token')))
    return render_template('superadmin/edit_usuario.html', usuario=usuario, empresas=empresas)


@superadmin_bp.route('/delete_usuario/<int:usuario_id>', methods=['POST'])
def delete_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    db.session.delete(usuario)
    db.session.commit()
    next_url = request.form.get('next') or request.args.get('next')
    if next_url:
        return redirect(next_url)
    return redirect(url_for('superadmin.dashboard', token=session.get('superadmin_token')))


@superadmin_bp.route('/create_column', methods=['GET', 'POST'])
def create_column():
    empresas = Empresa.query.all()
    if request.method == 'POST':
        name = request.form['name']
        empresa_id = int(request.form['empresa_id'])
        column = Column(name=name, empresa_id=empresa_id)
        db.session.add(column)
        db.session.commit()
        next_url = request.form.get('next') or request.args.get('next')
        if next_url:
            return redirect(next_url)
        return redirect(url_for('superadmin.dashboard', token=session.get('superadmin_token')))
    return render_template('superadmin/create_column.html', empresas=empresas)


@superadmin_bp.route('/edit_column/<int:column_id>', methods=['GET', 'POST'])
def edit_column(column_id):
    column = Column.query.get_or_404(column_id)
    empresas = Empresa.query.all()
    if request.method == 'POST':
        column.name = request.form['name']
        column.empresa_id = int(request.form['empresa_id'])
        db.session.commit()
        next_url = request.form.get('next') or request.args.get('next')
        if next_url:
            return redirect(next_url)
        return redirect(url_for('superadmin.dashboard', token=session.get('superadmin_token')))
    return render_template('superadmin/edit_column.html', column=column, empresas=empresas)


@superadmin_bp.route('/delete_column/<int:column_id>', methods=['POST'])
def delete_column(column_id):
    column = Column.query.get_or_404(column_id)
    db.session.delete(column)
    db.session.commit()
    next_url = request.form.get('next') or request.args.get('next')
    if next_url:
        return redirect(next_url)
    return redirect(url_for('superadmin.dashboard', token=session.get('superadmin_token')))
