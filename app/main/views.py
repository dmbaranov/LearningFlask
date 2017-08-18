from flask import render_template
from flask_login import current_user, fresh_login_required
from app.models import Post
from app.main import main


@main.route('/')
def main_page():
    return render_template('main/main_page.html', user=current_user)


@main.route('/dashboard')
@fresh_login_required
def dashboard_page():
    posts = Post.query.filter_by(author_id=current_user.id).all()

    return render_template('main/dashboard_page.html', posts=posts)


@main.route('/posts')
def posts_list_page():
    posts = Post.query.all()

    return render_template('main/posts_list_page.html', posts=posts)