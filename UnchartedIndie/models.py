from UnchartedIndies import database, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_usuario(id_usuario):
    return Usuario.query.get(int(id_usuario))

class Usuario(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    nome = database.Column(database.String, nullable=False)
    email = database.Column(database.String, nullable=False, unique=True)
    senha = database.Column(database.String, nullable=False)
    tipo_usuario = database.Column(database.String, nullable=False, default='default')
    foto_perfil = database.Column(database.String, default='default.jpg')
    data_perfil = database.Column(database.DateTime, nullable=False, default=datetime.utcnow)
    avaliacoes = database.relationship  ('Avaliacao', backref='criador', lazy=True)


class Jogo(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    nome_jogo = database.Column(database.String, nullable=False)
    ano_lanc = database.Column(database.Integer, nullable=False)
    nota_final = database.Column(database.Integer, nullable=False, default=0)
    desenvolvedora = database.Column(database.String, nullable=False)
    preco = database.Column(database.Integer, nullable=False)
    sinopse = database.Column(database.Text, nullable=False)
    categoria = database.Column(database.String, nullable=False)
    foto_jogo = database.Column(database.String, default='default.jpg')
    trailer = database.Column(database.String)
    avaliacoes = database.relationship('Avaliacao', backref='jogo', lazy=True)
    id_usuario = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)
    criacao = database.relationship('Usuario', backref='jogo_criador', lazy=True)

class Avaliacao(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    corpo = database.Column(database.Text, nullable=False)
    nota = database.Column(database.Integer, nullable=False)
    data_avaliacao   = database.Column(database.DateTime, nullable=False, default=datetime.utcnow)
    id_usuario = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)
    id_jogo = database.Column(database.Integer, database.ForeignKey('jogo.id'), nullable=False)