from . import db


class Empresa(db.Model):
    __tablename__ = 'empresas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    account_id = db.Column(db.String(120), unique=True, nullable=False)

    columns = db.relationship('Column', backref='empresa', cascade='all, delete', lazy=True)
    usuarios = db.relationship('Usuario', backref='empresa', cascade='all, delete', lazy=True)
    # campos customizáveis para cards: lista de definições {name, type}, até 8 itens
    custom_fields = db.Column(db.JSON, nullable=False, default=list)


class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), nullable=False)
    user_email = db.Column(db.String(120), nullable=False)
    user_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)

    cards = db.relationship('Card', backref='usuario', lazy=True)


class Column(db.Model):
    __tablename__ = 'columns'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)

    cards = db.relationship('Card', backref='column', cascade='all, delete', lazy=True)


class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(300))
    column_id = db.Column(db.Integer, db.ForeignKey('columns.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    # dados customizáveis do card conforme definições em Empresa.custom_fields
    custom_data = db.Column(db.JSON, nullable=False, default=dict)

