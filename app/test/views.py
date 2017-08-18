from app.test import test_b


@test_b.route('/test')
def test_page():
    return '<h1>Works!</h1>'
