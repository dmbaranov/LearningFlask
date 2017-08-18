from flask import render_template, redirect, url_for
from flask_login import current_user
from app.profile import profile
from app.models import User


@profile.route('/<username>')
def profile_page(username):
    user = User.query.filter_by(username=username).first()

    if user.id == current_user.id:
        return render_template('profile/my_profile_page.html', user=user)
    else:
        return render_template('profile/other_profile_page.html', user=user)
    # User not found
    return redirect(url_for('main.dashboard_page'))