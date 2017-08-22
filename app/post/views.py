from flask import request, redirect, flash, render_template, url_for
from flask_login import login_required, current_user
from app import db
from app.post import post
from app.post.forms import PostForm
from app.models import User, Post
import json


@post.route('/create-post/', methods=['GET', 'POST'])
@login_required
def create_post_page():
    form = PostForm(request.form)

    if request.method == 'POST':
        user = User.query.get(current_user.id)
        post = Post(form.title.data, form.content.data, user)

        db.session.add(post)
        db.session.commit()
        flash("Post has been successfully created", 'success')

        return redirect(url_for('main.dashboard_page'))
    return render_template('post/create_post_page.html', form=form)


@post.route('/post/<int:post_id>/')
def post_page(post_id):
    post = Post.query.get(post_id)

    return render_template('post/post_page.html', post=post)


@post.route('/post/<int:post_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit_post_page(post_id):
    form = PostForm(request.form)
    post = Post.query.get(post_id)

    if request.method == 'POST':
        if post.author_id == current_user.id:
            post.title = form.title.data
            post.content = form.content.data
            db.session.commit()

            return redirect(url_for('post.post_page', post_id=post.id))
        else:
            flash("You can't edit this post!", 'danger')
            return redirect(url_for('main.dashboard_page'))

    form.title.data = post.title
    form.content.data = post.content

    return render_template('post/edit_post_page.html', post=post, form=form)


@post.route('/delete-post/', methods=['POST'])
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