# Error Handling
import logging
from logging.handlers import SMTPHandler  # to send errors via email
from logging.handlers import RotatingFileHandler  # to create a log file
import os
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

app.config.from_object(Config)

# Database Initialization
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Register blueprints
from huntingfood.errors import bp as errors_bp
app.register_blueprint(errors_bp)

# protects all forms and request with csrf_token
# http://flask-wtf.readthedocs.io/en/stable/csrf.html
csrf = CSRFProtect(app)

from huntingfood import server, models, users


if not app.debug:
    # Error Handler to send emails
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    # Error handler to write a log file
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/' + __name__ + '.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Application startup')
