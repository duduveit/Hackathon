from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, IntegerField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from UnchartedIndies.models import Usuario
from flask_login import current_user


class FormCriarConta(FlaskForm):
    nome = StringField ("Nome Completo", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(6, 20)])
    confirmacao = PasswordField("Confirmação da senha", validators=[DataRequired(), EqualTo('senha')])
    enviar_cadastro = SubmitField("Criar Conta")

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError("E-mail já cadastrado. Cadastra-se com outro e-mail ou faça login para continuar")


class FormLogin(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(6, 20)])
    lembrar = BooleanField("Manter acesso")
    enviar_login = SubmitField("Fazer Login")


class FormEditarPerfil(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    foto_perfil = FileField("Atualizar foto de perfil", validators=[FileAllowed(['jpg', 'png'])])
    enviar_edicao = SubmitField("Confirmar edição")

    def validate_email(self, email):
        if current_user.email != email.data:
            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario:
                    raise ValidationError("E-mail cadastrado em outro usuário")


class FormCriarJogo(FlaskForm):
    nome = StringField("Nome do jogo", validators=[DataRequired()])
    ano_lancamento = IntegerField("Ano de lançamento", validators=[DataRequired()])
    desenvolvedora = StringField("Desenvolvedora", validators=[DataRequired()])
    preco = IntegerField("Preço de venda", validators=[DataRequired(), NumberRange(min=0)])
    sinopse = TextAreaField("Sinopse", validators=[DataRequired()])
    trailer = StringField("Link do trailer", validators=[DataRequired()])
    categoria = SelectField('Categorias', choices=[('Ação'), ('Aventura'), ('Luta'), ('Fps'), ('Corrida'), ('Simulação'), ('Esportes'), ('RPG'), ('Estratégia')])
    enviar_jogo = SubmitField("Criar jogo")


class FormAvaliarJogo(FlaskForm):
    corpo = TextAreaField("Comentário", validators=[DataRequired()])
    nota = IntegerField("Nota de avaliação", validators=[DataRequired(), NumberRange(min=0, max=100)])
    enviar_avaliacao = SubmitField("Enviar Comentário")