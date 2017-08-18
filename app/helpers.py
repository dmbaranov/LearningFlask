import binascii
import os
from flask import session, flash, redirect
from functools import wraps
from urllib.parse import urlparse, urljoin
from flask import request, url_for


def requires_login(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Login first', 'danger')
            return redirect(url_for('login_page'))
    return wrapper


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def generate_session_token():
    return str(binascii.hexlify(os.urandom(24)))


def j2_dateformat(value, dateformat='%H:%M / %d-%m-%Y'):
    return value.strftime(dateformat)