from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not all([name, email, password, confirm]):
            flash('Preencha todos os campos.', 'error')
            return render_template('auth/register.html')

        if password != confirm:
            flash('As senhas não coincidem.', 'error')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Este e-mail já está cadastrado.', 'error')
            return render_template('auth/register.html')

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        # First user becomes admin
        role = 'admin' if User.query.count() == 0 else 'estudante'
        user = User(name=name, email=email, password=hashed_pw, role=role)
        db.session.add(user)
        db.session.commit()

        flash(f'Conta criada com sucesso! Você é {"administrador" if role == "admin" else "aluno"}.', 'success')
        login_user(user)
        return redirect(url_for('main.dashboard'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash(f'Bem-vindo de volta, {user.name}!', 'success')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('E-mail ou senha incorretos.', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('auth.login'))
