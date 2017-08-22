from flask import render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from datetime import datetime
from app import app, db
from app.profile import profile
from app.models import User
from app.profile.forms import EditProfileForm
from app.profile.helpers import allowed_file
import os


@profile.before_request
def update_last_seen():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


# @profile.route('/', defaults={'username': getattr(current_user, 'username', '')})
@profile.route('/<username>/', methods=['GET', 'POST'])
def profile_page(username):
    user = User.query.filter_by(username=username).first()

    if user:
        form = EditProfileForm(user.username, request.form)

        # if there are no form data from the request, we take current value
        if not form.about_me.data:
            form.about_me.data = user.about_me

        if request.method == 'POST' and form.validate_on_submit():
            # TODO: add check if username is already exists
            user.username = form.username.data
            user.about_me = form.about_me.data
            db.session.commit()

        return render_template('profile/profile_page.html', user=user, form=form)

    # User not found
    return redirect(url_for('main.dashboard_page'))


@profile.route('/upload-avatar/', methods=['POST'])
@login_required
def upload_avatar():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part", 'danger')
            return redirect(url_for('profile.profile_page'))

        file = request.files['file']

        if file.filename == '':
            flash("You didn't select a file", 'danger')
            return redirect(url_for('profile.profile_page', username=current_user.username))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], current_user.username)

            if not os.path.exists(upload_path):
                os.makedirs(upload_path)

            file.save(os.path.join(upload_path, filename))
            current_user.avatar = filename
            db.session.commit()

            flash("Successfully uploaded a new avatar!", 'success')

            return redirect(url_for('profile.profile_page', username=current_user.username))
        else:
            flash("Only images are acceptable for the avatars", 'danger')
            return redirect(url_for('profile.profile_page', username=current_user.username))

    return redirect(url_for('profile.profile_page', username=current_user.username))


@profile.route('/follow/<user_id>/')
@login_required
def follow_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        flash("User not found", 'danger')
        return redirect(url_for('profile.profile_page', username=user.username))
    if user_id == current_user.id:
        flash("You can't follow yourself", 'danger')
        return redirect(url_for('profile.profile_page', username=user.username))
    make_follow = current_user.follow(user)
    if make_follow is None:
        flash("Cannot follow this user", 'danger')
        return redirect(url_for('profile.profile_page', username=user.username))

    db.session.add(make_follow)
    db.session.commit()

    flash("You're now following this user", 'success')
    return redirect(url_for('profile.profile_page', username=user.username))


@profile.route('/unfollow/<user_id>/')
@login_required
def unfollow_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        flash("User not found", 'danger')
        return redirect(url_for('profile.profile_page', username=user.username))
    if user_id == current_user.id:
        flash("You can't follow yourself", 'danger')
        return redirect(url_for('profile.profile_page', username=user.username))

    make_unfollow = current_user.unfollow(user)
    if make_unfollow is None:
        flash("Cannot follow this user", 'danger')
        return redirect(url_for('profile.profile_page', username=user.username))

    db.session.add(make_unfollow)
    db.session.commit()

    flash("You're now following this user", 'success')
    return redirect(url_for('profile.profile_page', username=user.username))