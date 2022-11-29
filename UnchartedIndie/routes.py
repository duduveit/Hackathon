from UnchartedIndies import app, database, bcrypt
from flask import render_template, redirect, url_for, flash, request, abort
from UnchartedIndies.forms import FormLogin, FormCriarConta, FormEditarPerfil, FormCriarJogo, FormAvaliarJogo
from UnchartedIndies.models import Usuario, Jogo, Avaliacao
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image



def salvar_imagem_perfil(imagem):
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + codigo + extensao
    caminho_completo = os.path.join(app.root_path, 'static/Fotos_perfil', nome_arquivo)
    tamanho = (400, 400)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)
    imagem_reduzida.save(caminho_completo)
    return nome_arquivo


@app.route("/", methods=['GET', 'POST']) #Caminho da página
def home():
    if request.method == "GET":
        lista_jogos = Jogo.query.all()
        foto_jogo = url_for('static', filename='foto_jogo/{}'.format('default.jpg'))
    return render_template("home.html", lista_jogos=lista_jogos, foto_jogo=foto_jogo)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = FormLogin()
    form_criarconta = FormCriarConta()
    if form_login.validate_on_submit() and 'enviar_login' in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha.encode('utf-8'), form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar.data)
            flash(f'Login feito com sucesso para o email: {form_login.email.data}', 'alert-success')
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('home'))
        else:
            flash(f'Email ou senha incorreto', 'alert-danger')

    if form_criarconta.validate_on_submit() and 'enviar_cadastro' in request.form:
        senha_cript = bcrypt.generate_password_hash(form_criarconta.senha.data).decode('utf-8')
        usuario = Usuario(nome=form_criarconta.nome.data, email=form_criarconta.email.data, senha=senha_cript)
        database.session.add(usuario)
        database.session.commit()
        flash(f'Cadastro feito com sucesso para o email: {form_criarconta.email.data}', 'alert-success')
        return redirect(url_for('home'))
    return render_template('login.html', form_login=form_login, form_criarconta=form_criarconta)


@app.route("/sair")
@login_required
def logout():
    logout_user()
    flash(f'Logout feito com sucesso')
    return redirect(url_for('home'))


@app.route('/perfil')
@login_required
def profile():
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('profile.html', foto_perfil=foto_perfil)


@app.route("/editar", methods=['GET', 'POST'])
@login_required
def edit():
    form = FormEditarPerfil()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.nome = form.nome.data
        if form.foto_perfil.data:
            imagem = salvar_imagem_perfil(form.foto_perfil.data)
            current_user.foto_perfil = imagem
        database.session.commit()
        flash(f'Perfil alterado com sucesso', 'alert-success')
        return redirect(url_for('profile'))
    elif request.method == "GET":
        form.nome.data = current_user.nome
        form.email.data = current_user.email
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('edit.html', foto_perfil=foto_perfil, form=form)


@app.route("/jogos", methods=['GET', 'POST'])
def games():
    if request.method == "GET":
        lista_jogos = Jogo.query.all()
        foto_jogo = url_for('static', filename='foto_jogo/{}'.format('default.jpg'))
    return render_template("games.html", lista_jogos=lista_jogos, foto_jogo=foto_jogo)


@app.route("/Jogo/<int:jogo_id>", methods=['GET', 'POST'])
def review(jogo_id):
    if request.method == "GET":
        jogo = Jogo.query.filter_by(id=jogo_id).first()
        avaliacoes = Avaliacao.query.filter_by(id_jogo=jogo.id).all()

    return render_template("review.html", jogo=jogo, avaliacoes=avaliacoes)


@app.route("/avaliacoes", methods=['GET', 'POST'])
def myposts():
    if request.method == "GET":
        usuario = current_user.id
        avaliacoes = Avaliacao.query.filter_by(id_usuario=usuario).all()
    return render_template("myposts.html", usuario=usuario, avaliacoes=avaliacoes)


@app.route("/avaliar/<int:jogo_id>", methods=['GET', 'POST'])
@login_required
def evaluate(jogo_id):
    form = FormAvaliarJogo()
    if 'enviar_avaliacao' in request.form:
        avaliacao = Avaliacao(corpo=form.corpo.data, nota=form.nota.data,
                              id_jogo=jogo_id, id_usuario=current_user.id)
        database.session.add(avaliacao)

        jogo = Jogo.query.filter_by(id=jogo_id).first()
        avaliacoes = Avaliacao.query.filter_by(id_jogo=jogo_id).all()
        soma=0
        for i, cat in enumerate(avaliacoes):
            soma += avaliacoes[i].nota

        media = soma // len(avaliacoes)
        jogo.nota_final=media
        database.session.commit()
        flash(f'Comentário realizado com sucesso', 'alert-success')
        return redirect(url_for('games'))
    return render_template("evaluate.html", form=form)


@app.route("/criar", methods=['GET', 'POST'])
@login_required
def creategame():
    form = FormCriarJogo()

    if 'enviar_jogo' in request.form:
        jogo = Jogo(nome_jogo=form.nome.data, ano_lanc=form.ano_lancamento.data,
                        desenvolvedora=form.desenvolvedora.data, preco=form.preco.data, sinopse=form.sinopse.data,
                        categoria=form.categoria.data, id_usuario=current_user.id, trailer=form.trailer.data)
        database.session.add(jogo)
        database.session.commit()
        flash(f'Criação do jogo {form.nome.data} concluída', 'alert-success')
        return redirect(url_for('creategame'))
    return render_template('create.html', form=form)


@app.route("/avaliacao-game/<int:avaliacao_id>", methods=['GET', 'POST'])
@login_required
def exibir_avaliacao(avaliacao_id):
    avaliacao = Avaliacao.query.get(avaliacao_id)
    form = FormAvaliarJogo()
    jogo = Jogo.query.filter_by(id=avaliacao.id_jogo).first()
    avaliacoes = Avaliacao.query.filter_by(id_jogo=jogo.id).all()
    if 'enviar_avaliacao' in request.form:
        avaliacao.corpo = form.corpo.data
        avaliacao.nota = form.nota.data
        soma = 0
        for i, cat in enumerate(avaliacoes):
            soma += avaliacoes[i].nota

        media = soma // len(avaliacoes)
        jogo.nota_final = media
        database.session.commit()
        flash("Avaliação atualizada com sucesso", 'alert-success')
        return redirect(url_for("home"))
    elif request.method == 'GET':
        form.corpo.data = avaliacao.corpo
        form.nota.data = avaliacao.nota
    return render_template('editevaluate.html', avaliacao=avaliacao, form=form)


@app.route("/avaliacao-game/<int:avaliacao_id>/excluir", methods=['GET', 'POST'])
@login_required
def excluir_avaliacao(avaliacao_id):
    avaliacao = Avaliacao.query.get(avaliacao_id)
    jogo = Jogo.query.filter_by(id=avaliacao.id_jogo).first()
    avaliacoes = Avaliacao.query.filter_by(id_jogo=avaliacao.id_jogo).all()

    if current_user == avaliacao.criador:
        database.session.delete(avaliacao)
        soma = 0
        for i, cat in enumerate(avaliacoes):
            soma += avaliacoes[i].nota

        media = soma // len(avaliacoes)
        jogo.nota_final = media
        database.session.commit()
        flash("Avaliação exluida com sucesso", 'alert-success')
        return redirect(url_for("home"))
    else:
        abort(403)