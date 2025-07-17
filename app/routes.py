from flask import Blueprint, render_template, request, redirect, url_for
from .models import db, Column, Card
from flask import jsonify

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    columns = Column.query.all()
    return render_template('index.html', columns=columns)

# Column CRUD
@main.route('/add_column', methods=['POST'])
def add_column():
    name = request.form['name']
    column = Column(name=name)
    db.session.add(column)
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/edit_column/<int:column_id>', methods=['POST'])
def edit_column(column_id):
    column = Column.query.get_or_404(column_id)
    column.name = request.form['name']
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/delete_column/<int:column_id>', methods=['POST'])
def delete_column(column_id):
    column = Column.query.get_or_404(column_id)
    db.session.delete(column)
    db.session.commit()
    return '', 204

@main.route('/add_card/<int:column_id>', methods=['POST'])
def add_card(column_id):
    title = request.form['title']
    description = request.form.get('description', '')
    card = Card(title=title, description=description, column_id=column_id)
    db.session.add(card)
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/edit_card/<int:card_id>', methods=['POST'])
def edit_card(card_id):
    card = Card.query.get_or_404(card_id)
    card.title = request.form['title']
    card.description = request.form.get('description', '')
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/delete_card/<int:card_id>', methods=['POST'])
def delete_card(card_id):
    card = Card.query.get_or_404(card_id)
    db.session.delete(card)
    db.session.commit()
    return '', 204  # Para AJAX deletar sem erro

@main.route('/move_card/<int:card_id>', methods=['POST'])
def move_card(card_id):
    card = Card.query.get_or_404(card_id)
    new_column_id = int(request.form['new_column_id'])
    card.column_id = new_column_id
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/api/move_card', methods=['POST'])
def api_move_card():
    data = request.get_json()
    card_id = int(data['card_id'])
    new_column_id = int(data['column_id'])
    card = Card.query.get_or_404(card_id)
    card.column_id = new_column_id
    db.session.commit()
    return jsonify({'success': True})