from flask import request, render_template, redirect, url_for, abort, flash
from flask_login import current_user, login_user, login_fresh, confirm_login, login_required, logout_user
from sqlalchemy import exc
from passlib.hash import sha256_crypt
from app import db
from app.auth import auth
from app.auth.forms import LoginForm, RegisterForm
from app.models import User
from app.helpers import generate_session_token, is_safe_url
import json


@auth.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm(request.form)

    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard_page'))

    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        # If this user exists in database
        if user:
            # If his password is correct
            if sha256_crypt.verify(form.password.data, user.password):
                # If he doesn't have a session_token yet
                if not user.session_token:
                    user.session_token = generate_session_token()
                    db.session.commit()

                login_user(user, remember=form.remember_me.data)
                next_url = request.args.get('next')

                if not is_safe_url(next_url):
                    return abort(400)

                return redirect(next_url or url_for('main.dashboard_page'))

            else:
                flash("Wrong password", "danger")
                return redirect(url_for('auth.login_page'))
        else:
            flash("This account doesn't exists", "danger")
            return redirect(url_for('auth.login_page'))

    return render_template('auth/login_page.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm(request.form)

    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard_page'))

    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))

        user = User(username=username, email=email, password=password)

        try:
            db.session.add(user)
            db.session.commit()
        except exc.IntegrityError:
            flash("This username or email already exists!", 'danger')
            db.session.rollback()
            return redirect(url_for('auth.register_page'))

        flash("You've successfully created an account!", 'success')
        login_user(user)

        return redirect(url_for('main.main_page'))

    return render_template('auth/register_page.html', form=form)


@auth.route('/relogin', methods=['GET', 'POST'])
def relogin():
    form = LoginForm(request.form)

    if not login_fresh():
        if (request.method == 'POST' and form.validate_on_submit()
                and sha256_crypt.verify(form.password.data, current_user.password)):
            confirm_login()
            next_url = request.args.get('next')

            if not is_safe_url(next_url):
                return abort(400)

            return redirect(next_url or url_for('main.dashboard_page'))

    form.username.data = current_user.username
    return render_template('auth.login_page.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been successfully logged out!", 'success')
    return redirect(url_for('main.main_page'))


@auth.route('/regenerate-session-token', methods=['POST'])
def regenerate_session_token():
    # Use this if you want to reset user's password
    new_token = generate_session_token()

    while User.query.filter_by(session_token=new_token).first():
        new_token = generate_session_token()

    current_user.session_token = str(new_token)
    db.session.commit()

    return json.dumps({'result': True})