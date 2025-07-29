from flask import Blueprint, render_template, request, redirect, url_for, g, abort, session
from ..models import db, Column, Card, Panel, Usuario
from flask import jsonify
from .auth import login_required, superadmin_required, has_panel_access

MAX_VALOR_NEGOCIADO = 9_999_999

main = Blueprint('main', __name__)


def build_custom_data(form):
    """Construct custom data dict from form based on empresa custom fields."""
    custom_data = {}
    for field in g.user.empresa.custom_fields:
        key = field.get('name')
        raw = form.get(f'custom_{key}')
        ftype = field.get('type')
        if ftype == 'number':
            try:
                val = float(raw)
            except (TypeError, ValueError):
                val = None
        elif ftype == 'boolean':
            val = bool(form.get(f'custom_{key}'))
        elif ftype == 'select':
            val = raw
        else:
            val = raw
        custom_data[key] = val
    return custom_data

@main.route('/', methods=['GET'])
@login_required
def index():
    empresa_id = session.get('empresa_id', g.user.empresa_id)

    # Determine allowed panels for the user
    if g.user.role == 'user':
        allowed_panels = [p for p in g.user.panels if p.empresa_id == empresa_id]
    else:
        allowed_panels = Panel.query.filter_by(empresa_id=empresa_id).all()

    panel_id = request.args.get('panel_id', type=int) or session.get('panel_id')

    if allowed_panels:
        allowed_ids = {p.id for p in allowed_panels}
        if panel_id not in allowed_ids:
            panel_id = allowed_panels[0].id
        session['panel_id'] = panel_id
        columns = (
            Column.query.join(Panel)
            .filter(Panel.empresa_id == empresa_id, Column.panel_id == panel_id)
            .all()
        )
        panel_user_ids = {u.id for u in Panel.query.get(panel_id).usuarios}
    else:
        session.pop('panel_id', None)
        columns = []
        panel_user_ids = set()

    # Filter cards
    for column in columns:
        if g.user.role == 'user':
            column.filtered_cards = [
                c
                for c in column.cards
                if c.vendedor_id is None or c.vendedor_id in panel_user_ids
            ]
        else:
            column.filtered_cards = list(column.cards)

        # Extra information used in the template
        column.cards_count = len(column.filtered_cards)
        column.valor_total = sum(
            card.valor_negociado or 0 for card in column.filtered_cards
        )

    # Definições de campos customizados (JSON) por empresa
    custom_fields = g.user.empresa.custom_fields
    vendedores = g.user.empresa.usuarios
    return render_template(
        'index.html',
        columns=columns,
        custom_fields=custom_fields,
        vendedores=vendedores,
        panels=allowed_panels,
        active_panel_id=panel_id,
    )

# Column CRUD
@main.route('/add_column', methods=['POST'])
@login_required
def add_column():
    name = request.form['name']
    panel_id = request.form.get('panel_id', type=int) or session.get('panel_id')
    panel = Panel.query.get(panel_id) if panel_id else None
    if panel and not has_panel_access(panel):
        return 'Acesso negado', 403
    column = Column(name=name, panel_id=panel_id)
    db.session.add(column)
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/edit_column/<int:column_id>', methods=['POST'])
@login_required
def edit_column(column_id):
    column = Column.query.get_or_404(column_id)
    if column.panel.empresa_id != g.user.empresa_id:
        abort(404)
    if column.panel and not has_panel_access(column.panel):
        return 'Acesso negado', 403
    column.name = request.form['name']
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/delete_column/<int:column_id>', methods=['POST'])
@login_required
def delete_column(column_id):
    column = Column.query.get_or_404(column_id)
    if column.panel.empresa_id != g.user.empresa_id:
        abort(404)
    if column.panel and not has_panel_access(column.panel):
        return 'Acesso negado', 403
    db.session.delete(column)
    db.session.commit()
    return '', 204

@main.route('/add_card/<int:column_id>', methods=['POST'])
@login_required
def add_card(column_id):
    column = Column.query.get_or_404(column_id)
    if column.panel.empresa_id != g.user.empresa_id:
        abort(404)
    panel = column.panel
    if panel and not has_panel_access(panel):
        return 'Acesso negado', 403
    # Campos fixos
    title = request.form['title']
    valor_negociado = request.form.get('valor_negociado', type=float)
    if valor_negociado is not None and valor_negociado > MAX_VALOR_NEGOCIADO:
        return 'Valor negociado acima do permitido', 400
    conversa = request.form.get('conversa')
    conversation_id = request.form.get('conversation_id')
    raw_vendedor = request.form.get('vendedor_id', type=int)
    vendedor_id = raw_vendedor if g.user.role == 'gestor' else g.user.id
    vendedor_id = vendedor_id or g.user.id
    if panel and vendedor_id and vendedor_id not in [u.id for u in panel.usuarios]:
        return 'Vendedor não pertence ao painel', 400
    # Monta dados customizados conforme definições em Empresa.custom_fields
    custom_data = build_custom_data(request.form)
    card = Card(
        title=title,
        valor_negociado=valor_negociado,
        conversa=conversa,
        conversation_id=conversation_id,
        column_id=column_id,
        vendedor_id=vendedor_id,
        custom_data=custom_data,
    )
    db.session.add(card)
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/edit_card/<int:card_id>', methods=['POST'])
@login_required
def edit_card(card_id):
    card = Card.query.get_or_404(card_id)
    if card.column.panel.empresa_id != g.user.empresa_id:
        abort(404)
    if card.column.panel and not has_panel_access(card.column.panel):
        return 'Acesso negado', 403
    if g.user.role != 'gestor':
        if card.vendedor_id not in (None, g.user.id):
            return 'Acesso negado', 403
        if card.vendedor_id is None:
            card.vendedor_id = g.user.id
    card.title = request.form['title']
    card.valor_negociado = request.form.get('valor_negociado', type=float)
    if card.valor_negociado is not None and card.valor_negociado > MAX_VALOR_NEGOCIADO:
        return 'Valor negociado acima do permitido', 400
    card.conversa = request.form.get('conversa')
    card.conversation_id = request.form.get('conversation_id')
    if g.user.role == 'gestor':
        novo_vendedor = request.form.get('vendedor_id', type=int)
        if novo_vendedor:
            panel = card.column.panel
            if panel and novo_vendedor not in [u.id for u in panel.usuarios]:
                return 'Vendedor não pertence ao painel', 400
            card.vendedor_id = novo_vendedor
    # Atualiza custom_data com os campos definidos
    custom_data = build_custom_data(request.form)
    card.custom_data = custom_data
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/delete_card/<int:card_id>', methods=['POST'])
@login_required
def delete_card(card_id):
    card = Card.query.get_or_404(card_id)
    if card.column.panel.empresa_id != g.user.empresa_id:
        abort(404)
    if card.column.panel and not has_panel_access(card.column.panel):
        return 'Acesso negado', 403
    if g.user.role != 'gestor' and card.vendedor_id not in (None, g.user.id):
        return 'Acesso negado', 403
    db.session.delete(card)
    db.session.commit()
    return '', 204  # Para AJAX deletar sem erro

@main.route('/move_card/<int:card_id>', methods=['POST'])
@login_required
def move_card(card_id):
    card = Card.query.get_or_404(card_id)
    if card.column.panel.empresa_id != g.user.empresa_id:
        abort(404)
    panel = card.column.panel
    if panel and not has_panel_access(panel):
        return 'Acesso negado', 403
    if g.user.role != 'gestor' and card.vendedor_id != g.user.id:
        return 'Acesso negado', 403
    new_column_id = int(request.form['new_column_id'])
    column = Column.query.get_or_404(new_column_id)
    if column.panel.empresa_id != g.user.empresa_id:
        abort(404)
    if column.panel and not has_panel_access(column.panel):
        return 'Acesso negado', 403
    if card.vendedor_id:
        panel = column.panel
        if panel and card.vendedor_id not in [u.id for u in panel.usuarios]:
            return 'Vendedor não pertence ao painel', 400
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
    if card.column.panel.empresa_id != g.user.empresa_id:
        return jsonify({'success': False}), 404
    if card.column.panel and not has_panel_access(card.column.panel):
        return jsonify({'success': False}), 403
    if g.user.role != 'gestor' and card.vendedor_id != g.user.id:
        return jsonify({'success': False}), 403
    column = Column.query.get_or_404(new_column_id)
    if column.panel.empresa_id != g.user.empresa_id:
        return jsonify({'success': False}), 404
    if column.panel and not has_panel_access(column.panel):
        return jsonify({'success': False}), 403
    if card.vendedor_id:
        panel = column.panel
        if panel and card.vendedor_id not in [u.id for u in panel.usuarios]:
            return jsonify({'success': False}), 400
    card.column_id = new_column_id
    db.session.commit()
    return jsonify({'success': True})


@main.route('/select_panel', methods=['POST'])
@login_required
def select_panel():
    """Update the selected panel in the user session."""
    panel_id = request.form.get('panel_id', type=int)
    empresa_id = session.get('empresa_id', g.user.empresa_id)
    if g.user.role == 'user':
        allowed_panels = [p for p in g.user.panels if p.empresa_id == empresa_id]
    else:
        allowed_panels = Panel.query.filter_by(empresa_id=empresa_id).all()
    allowed_ids = {p.id for p in allowed_panels}
    if panel_id in allowed_ids:
        session['panel_id'] = panel_id
    return redirect(url_for('main.index'))


@main.route('/toggle_theme', methods=['POST'])
@login_required
def toggle_theme():
    """Flip the dark_mode setting for the logged user's company."""
    empresa = g.user.empresa
    empresa.dark_mode = not empresa.dark_mode
    db.session.commit()
    return jsonify({'success': True, 'dark_mode': empresa.dark_mode})
