from flask import render_template
from huntingfood import db
from huntingfood.models import User
from huntingfood.errors import bp
from flask_wtf.csrf import CSRFError

@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500


@bp.app_errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('errors/csrf_error.html', reason=e.description), 400


@bp.route('/test_error500')
def testError500():
    newUser = User(name='admin', email='admin@huntingfood.com')
    db.session.add(newUser)
    db.session.commit()
