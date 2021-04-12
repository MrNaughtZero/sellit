from webapp.utils.login_decorator import loggedout_required, developer_required
from webapp.utils.tools import validate_dob
from webapp.forms import RegisterForm, LoginForm, PasswordResetForm
from webapp.models import User, Verification
from flask import Blueprint, render_template, url_for, flash, get_flashed_messages, redirect, request, abort
from flask_login import login_user, logout_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/register', methods=['GET'], subdomain='auth')
@developer_required
@loggedout_required
def register() -> render_template:
    return render_template('/auth/register.html', form=RegisterForm(), flashed_message=get_flashed_messages())

@auth_bp.route('/register/user', methods=['POST'], subdomain='auth')
@developer_required
@loggedout_required
def register_user() -> redirect:
    form = RegisterForm()
    
    if not form.validate_on_submit():
        flash(list(form.errors.values())[0])
        return redirect(url_for('auth.register'))

    if User().query.filter_by(email=request.form.get('email')).first():
        flash(['''Email is already registered. Please use a different email, or login to continue'''])
        return redirect(url_for('auth.register'))

    if User().query.filter_by(username=request.form.get('username')).first():
        flash(['Username is taken. Please choose another username.'])
        return redirect(url_for('auth.register'))

    if not validate_dob(request.form.get('date_of_birth')):
        flash(['You must be at least 13 years old to use Sellit.'])
        return redirect(url_for('auth.register'))

    User().create_user(request.form)
    
    flash(['Account created. Please check your email to activate your account'])
    return redirect(url_for('auth.login'))

@auth_bp.route('/email/verify/<string:email_code>', methods=['GET'], subdomain='auth')
@developer_required
@loggedout_required
def verify_email(email_code) -> redirect:
    if not User().activate_account(email_code):
        return abort(404)
    
    flash(['Your account has been verified. Please login to continue'])
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET'], subdomain='auth')
@developer_required
@loggedout_required
def login() -> render_template:    
    return render_template('/auth/login.html', flashed_message=get_flashed_messages(), form=LoginForm())

@auth_bp.route('/login/user', methods=['POST'], subdomain='auth')
@developer_required
@loggedout_required
def login_attempt() -> redirect:
    form = LoginForm()
    
    if not form.validate_on_submit():
        flash(list(form.errors.values())[0])
        return redirect(url_for('auth.login'))

    query = User().check_credentials(request.form.get('email'), request.form.get('password'))
    
    if not query:
        flash(['Incorrect login details'])
        return redirect(url_for('auth.login'))
    
    if query.verification.email_code:
        update_code = Verification().update_verification(query.uuid)

        flash(['Your account has not been activated. Another email has been sent'])
        return redirect(url_for('auth.login'))
    
    login_user(query)
    return redirect(url_for('dashboard.home'))

@auth_bp.route('/logout', methods=['GET'], subdomain='auth')
@developer_required
def logout() -> render_template:
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgotten/password', methods=['GET'], subdomain='auth')
@developer_required
@loggedout_required
def forgotten_password() -> render_template:
    return render_template('/auth/reset-password.html', form=PasswordResetForm(), flashed_message=get_flashed_messages())

@auth_bp.route('/reset/password/submit', methods=['POST'], subdomain='auth')
@developer_required
@loggedout_required
def check_email_password() -> redirect:
    form = PasswordResetForm()
    
    if not form.validate_on_submit():
        flash(list(form.errors.values())[0])
    
    User().password_reset(request.form.get('email'))
    
    flash(['If your email exists, you will receive a password reset email shortly'])
    return redirect(url_for('auth.login'))

@auth_bp.route('/reset/password/<string:password_code>', methods=['GET'], subdomain='auth')
@developer_required
@loggedout_required
def reset_password(password_code) -> redirect:
    if not User().set_new_password(password_code):
        flash(['Something went wrong. Please try again'])
        return redirect(url_for('auth.forgotten_password'))
    
    flash(['Your password has been successfully reset. Check your email for your new password'])
    return redirect(url_for('auth.login'))