import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fjsd87fsd002WuJJ3&$kflsdf'
    DEBUG = True # Turns on debugging features in Flask
    BCRYPT_LOG_ROUNDS = 12 # Configuration for the Flask-Bcrypt extension
    MAIL_FROM_EMAIL = 'info@example.com' # For use in application emails
    UPLOAD_FOLDER = 'huntingfood/upload'
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # limit to 2MB
    ALLOWED_EXTENSIONS = {'png', 'png', 'jpg', 'jpeg', 'gif'}
    SQLALCHEMY_DATABASE_URI = os.environ.get('DB_CONNECTION') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
