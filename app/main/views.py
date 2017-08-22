from flask import render_template, redirect, url_for
from flask_login import current_user, fresh_login_required
from sqlalchemy import exc
from app import app
from app.models import Post
from app.main import main
import math


@main.route('/')
def main_page():
    return render_template('main/main_page.html', user=current_user)


@main.route('/dashboard/')
@fresh_login_required
def dashboard_page():
    posts = Post.query.filter_by(author_id=current_user.id).all()
    followed_posts = current_user.followed_posts().all()

    return render_template('main/dashboard_page.html', posts=posts, followed_posts=followed_posts)


@main.route('/posts/')
@main.route('/posts/<int:page>/')
def posts_list_page(page=1):
    posts_per_page = app.config['POSTS_PER_PAGE']

    try:
        posts = Post.query.paginate(page, posts_per_page, False)
    except exc.DataError:
        return redirect(url_for('main.posts_list_page'))

    if page > posts.pages:
        return redirect(url_for('main.posts_list_page', page=posts.pages))

    return render_template('main/posts_list_page.html', posts=posts)
