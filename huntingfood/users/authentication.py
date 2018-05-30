import json
from flask import render_template, request, redirect, abort, make_response, flash, url_for, jsonify
from huntingfood import app
from huntingfood import db
from huntingfood.models import User, UserGroup, UserGroupAssociation, Inventory, DietPlan, ConsumptionPlan
from urllib.parse import urlparse
from oauth2client.client import OAuth2WebServerFlow  # flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import requests

# required to create a wrapper function for authentication
from functools import wraps

from flask import session as login_session


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


def login_required(func):

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if 'user_id' not in login_session:
            return login()
        else:
            return func(*args, **kwargs)
    return decorated_view


# User Functions
def createUser(login_session, password):
    if (login_session['provider'] == 'local'):
        newUser = User(
            name=login_session['name'],
            email=login_session['email'],
            provider=login_session['provider'],
            language='DE')  # TODO: Fetch default settings from an additional user setting page after registration
        print('Create new local user')
        newUser.hash_password(password)
        db.session.add(newUser)
        db.session.commit()
    else:
        newUser = User(
            name=login_session['name'],
            email=login_session['email'],
            picture=login_session['picture'],
            provider=login_session['provider'],
            provider_id=login_session['provider_id'],
            language='DE')
        db.session.add(newUser)
        db.session.commit()

    # Initialize required data sets
    setUserDefaults(newUser.id)

    return newUser


def setUserDefaults(user_id):
    user = User.query.filter_by(id=user_id).one()

    if not user.default_inventory_id:
        print('No default inventory found')
        inventory = createInventory(user_id)
        user.default_inventory_id = inventory.id

    if not user.default_diet_plan_id:
        print('No default dietplan found')
        diet_plan = createDietPlan(user_id)
        user.default_diet_plan_id = diet_plan.id

    if not user.default_consumption_plan_id:
        print('No default consumption plan found')
        consumption_plan = createConsumptionPlan(user_id)
        user.default_consumption_plan_id = consumption_plan.id

    db.session.commit()


def createDietPlan(user_id):

    obj_diet_plan = DietPlan(
        creator_id=user_id)
    db.session.add(obj_diet_plan)
    db.session.commit()

    return obj_diet_plan


def createConsumptionPlan(user_id):

    obj_consumption_plan = ConsumptionPlan(
        creator_id=user_id)
    db.session.add(obj_consumption_plan)
    db.session.commit()

    return obj_consumption_plan


def createInventory(user_id):
    obj_inventory = Inventory(
        creator_id=user_id)
    db.session.add(obj_inventory)
    db.session.commit()

    return obj_inventory


def createUserGroup(user_id):

    newUserGroup = UserGroup(name="Group1")
    a = UserGroupAssociation(is_owner=True)
    a.user = User.query.filter_by(id=user_id).one()
    newUserGroup.users.append(a)

    db.session.add(newUserGroup)
    db.session.commit()

    return newUserGroup.id


def listUsersInGroup(group_id):
    g = UserGroup.query.filter_by(id=group_id).one()

    for assoc in g.users:
        print(assoc.user.name)


# Retrieves the user object
def getUserInfo(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    return user


# Retrieves the user id based on an email
# TODO: Is this function redundant cause of getUser?
def getUserID(email):
    try:
        user = User.query.filter_by(email=email).one()
        return user.id
    except:
        return None


# Retrieves the user id based on an email
def getUserGroupID(user_id):
    try:
        user_group = UserGroup.query.filter_by(owner=user_id).one()
        return user_group.id
    except:
        return None


# Retrieves the user based on an email
def getUser(email):
    try:
        user = User.query.filter_by(email=email).one()
        return user
    except:
        return None


def validateUser(login_session):
    '''
    After successfuly 3rd party authentication checks if user
    is authorized to access the application. Creates a user object if
    necessary.
    '''
    # Validates if user exists and creates if necessary
    print("ValidateUser with login_session[email] = " + login_session['email'])
    user = getUser(login_session['email'])
    # response values
    # 0 = not authorized
    # 1 = existing user authorized
    # 2 = newly created user authorized
    response = 0
    if not user:
        password = None
        print("Create a new user ...")
        user = createUser(login_session, password)
        response = 1
    if not user.active:
        response = 0
        return response  # user is not authorized
    else:
        login_session['user_id'] = user.id
        login_session['provider'] = user.provider
        login_session['language'] = user.language
        login_session['default_diet_plan_id'] = user.default_diet_plan_id
        login_session['default_inventory_id'] = user.default_inventory_id
        login_session['default_consumption_plan_id'] = user.default_consumption_plan_id
        response = response + 1
        return response  # user is authorized


def welcome():
    output = ''
    output += '<h1>Welcome, '
    output += login_session['name']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;" \
        "-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    return output


@app.route('/login', methods=['GET', 'POST'])
def showLogin():
    if request.method == 'GET':
        return login()
    elif request.method == 'POST':
        login_session['email'] = request.form['email']
        password = request.form['password']
        user = getUser(login_session['email'])
        if not user:
            return login("Unknown username or incorrect password")
        else:
            if user.verify_password(password) and (validateUser(login_session) > 0):
                return redirect('/')
            else:
                return login("Unknown username or incorrect password")


@app.route('/register', methods=['GET', 'POST'])
def showRegister():
    if request.method == 'GET':
        return render_template("register.html")
    elif request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if username is None or email is None or password is None:
            abort(400)
        if 'email' in login_session.keys():
            abort(400)  # existing User
        else:
            login_session['name'] = username
            login_session['email'] = email
            login_session['provider'] = 'local'
            user = createUser(login_session, password)
            status = validateUser(login_session)
            if (status == 2):
                return redirect(url_for("showSettings"))
            else:
                return redirect('/')
    return redirect('/')


@app.route('/user/settings', methods=['GET', 'POST'])
@login_required
def showSettings():
    user_id = login_session['user_id']
    user = getUserInfo(user_id)
    if request.method == 'GET':
        return render_template(
            "settings.html",
            user=user,
            data_portions=app.config['DATA_PORTIONS'])
    elif request.method == 'POST':
        default_portions = request.form['default_portions']
        city = request.form['city']
        zip = request.form['zip']
        street = request.form['street']
        state = request.form['state']
        user.default_portions = default_portions
        user.city = city
        user.zip = zip
        user.street = street
        user.state = state
        db.session.commit()
    return redirect('/')


@app.route('/api/v1/users', methods=['GET'])
def api_v1_users():
    if request.method == 'GET':
        if 'user_id' in login_session:
            user_id = login_session['user_id']
            user = getUserInfo(user_id)
        return jsonify(users=[user.serialize])


@app.route('/gconnect', methods=['POST'])
def gconnect():

    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = OAuth2WebServerFlow(
            client_id=app.config['GOOGLE_WEB_CLIENT_ID'],
            client_secret=app.config['GOOGLE_CLIENT_SECRET'],
            scope='',
            redirect_uri='postmessage')

        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        print("Failed to upgrade the authorization code")
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != app.config['GOOGLE_WEB_CLIENT_ID']:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['provider_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['name'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # Validate user against database
    status = validateUser(login_session)
    print('user status = ' + str(status))
    if (status == 1):
        output = welcome()
        flash("Now logged in as %s" % login_session['name'])
        return jsonify(status='1', output=output)
    elif (status == 2):
        output = welcome()
        flash("Now logged in as %s" % login_session['name'])
        return jsonify(status='2', output=output)
    else:
        flash('User is not authorized to access this application')
        return False


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

        # TODO: Logout / disconnect does not work correctly unless
        # the browser is closed / the cookie is no longer valid
        # at the moment it will show as failed to revoke token
        # with a status 400 from google
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/fbconnect', methods=['POST'])
def fbconnect():

    access_token = request.data.decode("utf-8")
    url = 'https://graph.facebook.com/oauth/access_token?' \
        'grant_type=fb_exchange_token&client_id=%s&' \
        'client_secret=%s&fb_exchange_token=%s' % (app.config['FACEBOOK_APP_ID'],
                                                   app.config['FACEBOOK_SECRET_KEY'],
                                                   access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1].decode("utf-8")

    # Use token to get user info from API
    # userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token
        exchange we have to split the token first on commas and select the
        first index which gives us the key : value for the server access token
        then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used
        directly in the graph api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me' \
        '?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['name'] = data["name"]
    login_session['email'] = data["email"]
    login_session['provider_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture' \
        '?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # Validate user against database
    status = validateUser(login_session)
    if (status == 1):
        output = welcome()
        flash("Now logged in as %s" % login_session['name'])
        return jsonify(status='1', output=output)
    elif (status == 2):
        output = welcome()
        flash("Now logged in as %s" % login_session['name'])
        return jsonify(status='2', output=output)
    else:
        flash('User is not authorized to access this application')
        return False


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['provider_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' \
        % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['provider_id']
            del login_session['access_token']
            del login_session['picture']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['provider_id']
            del login_session['picture']
        del login_session['name']
        del login_session['email']
        del login_session['user_id']
        del login_session['provider']
        print("You have successfully been logged out.")
        return redirect('/')
    else:
        print("You were not logged in")
        return redirect('/')
