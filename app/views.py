from flask import request, render_template, flash, redirect, url_for, abort
from flask_login import login_user, logout_user, current_user, login_required, login_fresh, fresh_login_required, confirm_login
from sqlalchemy import exc
from passlib.hash import sha256_crypt
from app import app, db, lm
from app.forms import LoginForm, RegisterForm, PostForm
from app.models import User, Post
from app.helpers import is_safe_url, generate_session_token
import json


@lm.user_loader
def get_user(session_token):
    return User.query.filter_by(session_token=session_token).first()


@app.route('/')
def main_page():
    return render_template('main_page.html', user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm(request.form)

    if current_user.is_authenticated:
        return redirect(url_for('dashboard_page'))

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

                return redirect(next_url or url_for('dashboard_page'))

            else:
                flash("Wrong password", "danger")
                return redirect(url_for('login_page'))
        else:
            flash("This account doesn't exists", "danger")
            return redirect(url_for('login_page'))

    return render_template('login_page.html', form=form)


@app.route('/relogin', methods=['GET', 'POST'])
def relogin():
    form = LoginForm(request.form)

    if not login_fresh():
        if (request.method == 'POST' and form.validate_on_submit()
                and sha256_crypt.verify(form.password.data, current_user.password)):
            confirm_login()
            next_url = request.args.get('next')

            if not is_safe_url(next_url):
                return abort(400)

            return redirect(next_url or url_for('dashboard_page'))

    form.username.data = current_user.username
    return render_template('login_page.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():
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
            return redirect(url_for('register_page'))

        flash("You've successfully created an account!", 'success')
        login_user(user)

        return redirect(url_for('main_page'))

    return render_template('register_page.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been successfully logged out!", 'success')
    return redirect(url_for('main_page'))


@app.route('/dashboard')
@login_required
@fresh_login_required
def dashboard_page():
    posts = Post.query.filter_by(author_id=current_user.id).all()

    return render_template('dashboard_page.html', posts=posts)


@app.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post_page():
    form = PostForm(request.form)

    if request.method == 'POST':
        user = User.query.get(current_user.id)
        post = Post(form.title.data, form.content.data, user)

        db.session.add(post)
        db.session.commit()
        flash("Post has been successfully created", 'success')

        return redirect(url_for('dashboard_page'))
    return render_template('create_post_page.html', form=form)


@app.route('/post/<int:post_id>')
def post_page(post_id):
    post = Post.query.get(post_id)

    return render_template('post_page.html', post=post)


@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post_page(post_id):
    form = PostForm(request.form)
    post = Post.query.get(post_id)

    if request.method == 'POST':
        if post.author_id == current_user.id:
            post.title = form.title.data
            post.content = form.content.data
            db.session.commit()

            return redirect(url_for('post_page', post_id=post.id))
        else:
            flash("You can't edit this post!", 'danger')
            return redirect(url_for('dashboard_page'))

    form.title.data = post.title
    form.content.data = post.content

    return render_template('edit_post_page.html', post=post, form=form)


@app.route('/delete-post', methods=['POST'])
@login_required
def delete_post():
    post_id = request.json['postId']
    post = Post.query.get(post_id)

    if post.author_id == current_user.id:
        db.session.delete(post)
        db.session.commit()

        flash("Post have been successfully deleted", 'success')

        return json.dumps({'result': True})
    else:
        flash("You can't delete this post!", 'danger')

        return json.dumps({'result': False})


@app.route('/posts')
def posts_list_page():
    posts = Post.query.all()

    return render_template('posts_list_page.html', posts=posts)


@app.route('/test', methods=['POST'])
def regenerate_session_token():
    new_token = generate_session_token()

    while User.query.filter_by(session_token=new_token).first():
        new_token = generate_session_token()

    current_user.session_token = str(new_token)
    db.session.commit()

    return json.dumps({'result': True})
