from flask import Blueprint, render_template, request, redirect, url_for, g, abort
from .models import db, Column, Card
from flask import jsonify
from .auth import login_required, gestor_required

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    columns = Column.query.filter_by(empresa_id=g.user.empresa_id).all()
    return render_template('index.html', columns=columns)

# Column CRUD
@main.route('/add_column', methods=['POST'])
@login_required
@gestor_required
def add_column():
    name = request.form['name']
    column = Column(name=name, empresa_id=g.user.empresa_id)
    db.session.add(column)
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/edit_column/<int:column_id>', methods=['POST'])
@login_required
@gestor_required
def edit_column(column_id):
    column = Column.query.get_or_404(column_id)
    if column.empresa_id != g.user.empresa_id:
        abort(404)
    column.name = request.form['name']
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/delete_column/<int:column_id>', methods=['POST'])
@login_required
@gestor_required
def delete_column(column_id):
    column = Column.query.get_or_404(column_id)
    if column.empresa_id != g.user.empresa_id:
        abort(404)
    db.session.delete(column)
    db.session.commit()
    return '', 204

@main.route('/add_card/<int:column_id>', methods=['POST'])
@login_required
def add_card(column_id):
    column = Column.query.get_or_404(column_id)
    if column.empresa_id != g.user.empresa_id:
        abort(404)
    title = request.form['title']
    description = request.form.get('description', '')
    card = Card(
        title=title,
        description=description,
        column_id=column_id,
        usuario_id=g.user.id,
    )
    db.session.add(card)
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/edit_card/<int:card_id>', methods=['POST'])
@login_required
def edit_card(card_id):
    card = Card.query.get_or_404(card_id)
    if card.column.empresa_id != g.user.empresa_id:
        abort(404)
    if g.user.role != 'gestor' and card.usuario_id != g.user.id:
        return 'Acesso negado', 403
    card.title = request.form['title']
    card.description = request.form.get('description', '')
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/delete_card/<int:card_id>', methods=['POST'])
@login_required
def delete_card(card_id):
    card = Card.query.get_or_404(card_id)
    if card.column.empresa_id != g.user.empresa_id:
        abort(404)
    if g.user.role != 'gestor' and card.usuario_id != g.user.id:
        return 'Acesso negado', 403
    db.session.delete(card)
    db.session.commit()
    return '', 204  # Para AJAX deletar sem erro

@main.route('/move_card/<int:card_id>', methods=['POST'])
@login_required
def move_card(card_id):
    card = Card.query.get_or_404(card_id)
    if card.column.empresa_id != g.user.empresa_id:
        abort(404)
    if g.user.role != 'gestor' and card.usuario_id != g.user.id:
        return 'Acesso negado', 403
    new_column_id = int(request.form['new_column_id'])
    column = Column.query.get_or_404(new_column_id)
    if column.empresa_id != g.user.empresa_id:
        abort(404)
    card.column_id = new_column_id
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/api/move_card', methods=['POST'])
@login_required
def api_move_card():
    data = request.get_json()
    card_id = int(data['card_id'])
    new_column_id = int(data['column_id'])
    card = Card.query.get_or_404(card_id)
    if card.column.empresa_id != g.user.empresa_id:
        return jsonify({'success': False}), 404
    if g.user.role != 'gestor' and card.usuario_id != g.user.id:
        return jsonify({'success': False}), 403
    column = Column.query.get_or_404(new_column_id)
    if column.empresa_id != g.user.empresa_id:
        return jsonify({'success': False}), 404
    card.column_id = new_column_id
    db.session.commit()
    return jsonify({'success': True})
