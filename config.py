import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fjsd87fsd002WuJJ3&$kflsdf'
    # Turns on debugging features in Flask
    DEBUG = True
    # Configuration for the Flask-Bcrypt extension
    BCRYPT_LOG_ROUNDS = 12
    # File upload
    UPLOAD_FOLDER = 'huntingfood/upload'
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # limit to 2MB
    ALLOWED_EXTENSIONS = {'png', 'png', 'jpg', 'jpeg', 'gif'}
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DB_CONNECTION') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Mail Server setup
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_FROM_EMAIL = 'info@huntingfood.com'  # For use in application emails
    ADMINS = ['mailboxsoeren@gmail.com']
    # Google Cloud Service Account Credentials
    GOOGLE_CLOUD_CREDENTIALS_PK = os.environ.get('GOOGLE_CLOUD_CREDENTIALS_PK')
    # Google oauth credentials
    GOOGLE_WEB_CLIENT_ID = os.environ.get('GOOGLE_WEB_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    # Google api key (used for maps), "WTF" required to resolve bug in h.terminal
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY_WTF')
    # Facebook oauth credentials
    FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')
    FACEBOOK_SECRET_KEY = os.environ.get('FACEBOOK_SECRET_KEY')
    # NDB connection
    NDB_KEY = os.environ.get('NDB_KEY')
