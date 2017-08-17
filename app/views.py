from flask import request, render_template, flash, redirect, url_for, session, g, abort
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import exc
from passlib.hash import sha256_crypt
import json
from app import app, db, lm
from app.forms import LoginForm, RegisterForm, PostForm
from app.models import User, Post
from app.helpers import is_safe_url


@lm.user_loader
def get_user(user_id):
    return User.query.get(int(user_id))


@app.before_request
def before_request():
    g.user = current_user


@app.route('/')
def main_page():
    # user = None
    # if hasattr(session, 'logged_in') and session['logged_in']:
    #     user = User.query.filter_by(id=session['user_id']).first()
    return render_template('main_page.html', user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm(request.form)

    # if 'user' in g and g.user._is_authenticated:
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('dashboard_page'))

    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(username=form.username.data).first()

        if user:
            if sha256_crypt.verify(form.password.data, user.password):
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


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))

        user = User(username=username, email=email, password=password)
        print(user.email)

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
def dashboard_page():
    posts = Post.query.filter_by(author_id=current_user.id).all()

    return render_template('dashboard_page.html', posts=posts)


@app.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post_page():
    form = PostForm(request.form)

    if request.method == 'POST':
        user = User.query.filter_by(id=current_user.id).first()
        post = Post(form.title.data, form.content.data, user)

        db.session.add(post)
        db.session.commit()
        flash("Post has been successfully created", 'success')

        return redirect(url_for('dashboard_page'))
    return render_template('create_post_page.html', form=form)


@app.route('/post/<int:post_id>')
def post_page(post_id):
    post = Post.query.filter_by(id=post_id).first()

    return render_template('post_page.html', post=post)


@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post_page(post_id):
    form = PostForm(request.form)
    post = Post.query.filter_by(id=post_id).first()

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
    post = Post.query.filter_by(id=post_id).first()

    if post.author_id == current_user.id:
        Post.query.filter_by(id=post_id).delete()
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
