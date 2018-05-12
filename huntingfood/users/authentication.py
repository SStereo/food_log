from flask import render_template, request
from huntingfood import app
from urllib.parse import urlparse


def login(*args):
    if args:
        message = args[0]
    else:
        message = None

    if request.referrer:
        previous_url = urlparse(request.referrer)[2]
    else:
        previous_url = '/'
    target_url = request.url
    if not target_url or previous_url == '/':
        target_url = '/'
    return render_template(
        "login.html",
        G_CLIENT_ID=app.config['GOOGLE_WEB_CLIENT_ID'],
        F_APP_ID=app.config['FACEBOOK_APP_ID'],
        redirect_next=target_url,
        message=message)
