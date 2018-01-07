import os  # required to have access to the Port environment variable
import json

# Google cloud authentication & configuration
from oauth2client.client import GoogleCredentials
from google.oauth2 import service_account

from google.cloud import translate  # for google translator api
from google.cloud import language  # for google natural language api

# added due to google oauth login feature
from oauth2client.client import OAuth2WebServerFlow  # flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from flask import make_response
import requests
import random, string
from flask import session as login_session  # a dictionary to store information

# National Nutrient Database - United States Department of Agriculture
import ndb

from datetime import datetime  #required for method "now" for file name change
from flask import Flask, render_template, request, url_for, redirect, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename  #required for file upload
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from food_database import (Base,
                   User,
                   UOM,
                   Meal,
                   Ingredient,
                   Food,
                   FoodComposition,
                   Nutrient,
                   ShoppingListItem,
                   FoodMainGroup)

# Application Settings
UPLOAD_FOLDER = 'upload'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.secret_key = "ABC123"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database connection
DB_CONNECTION = os.environ.get('DB_CONNECTION')
engine = create_engine(DB_CONNECTION)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Google Cloud Connection
PK = os.environ.get('GOOGLE_CLOUD_CREDENTIALS_PK')
jsonString = """{
  "type": "service_account",
  "project_id": "long-memory-188919",
  "private_key_id": "b26b39e14a2375751b5064b77e426243b4625de4",
  "private_key": \""""+PK+"""\",
  "client_email": "serviceaccount-owner@long-memory-188919.iam.gserviceaccount.com",
  "client_id": "106478515271128625146",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://accounts.google.com/o/oauth2/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/serviceaccount-owner%40long-memory-188919.iam.gserviceaccount.com"
}"""
service_account_info = json.loads(jsonString)
google_cloud_credentials = service_account.Credentials.from_service_account_info(
    service_account_info)

# Google translate client
translate_client = translate.Client(target_language='en',credentials=google_cloud_credentials)

# Google natural language client
language_client = language.LanguageServiceClient(credentials=google_cloud_credentials)

# Google oauth credentials
GOOGLE_WEB_CLIENT_ID = os.environ.get('GOOGLE_WEB_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

# Facebook oauth credentials
FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')
FACEBOOK_SECRET_KEY = os.environ.get('FACEBOOK_SECRET_KEY')

# NDB connection
NDB_KEY = os.environ.get('NDB_KEY')

# TODO: Validate if there is a better way in sqlAlchemy ot achieve that
# TODO: Ensure reload of dictionary when uom table changes
nutrientDict = {}
items = session.query(Nutrient)
for i in items:
    nutrientDict.update({i.titleEN:i.id})

uomDict = {}
items = session.query(UOM)
for i in items:
    uomDict.update({i.uom:i.type})

# Custom Static folders
@app.route('/css/<path:filename>')
def css_static(filename):
    return send_from_directory('css', filename)

@app.route('/js/<path:filename>')
def js_static(filename):
    return send_from_directory('js', filename)

@app.route('/font/<path:filename>')
def font_static(filename):
    return send_from_directory('font', filename)

@app.route('/img/<path:filename>')
def img_static(filename):
    return send_from_directory('img', filename)

@app.route('/sass/<path:filename>')
def sass_static(filename):
    return send_from_directory('sass', filename)

@app.route('/upload/<path:filename>')
def upload_static(filename):
    return send_from_directory('upload', filename)

# Application Routes

@app.route('/login')
def showLogin():
    # Generate a random session id and pass it to the login template
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    return render_template("login.html", STATE=state, CLIENT_ID=GOOGLE_WEB_CLIENT_ID)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        # TODO: Replace json file with path variable?
        #oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        #oauth_flow.redirect_uri = 'postmessage'
        oauth_flow = OAuth2WebServerFlow(client_id=GOOGLE_WEB_CLIENT_ID,
                           client_secret=GOOGLE_CLIENT_SECRET,
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
    if result['issued_to'] != GOOGLE_WEB_CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # Validates if user already exists in the database
    # if not it creates a new account in the Database
    if not getUserID(login_session['email']):
        createUser(login_session)

    login_session['user_id'] = getUserID(login_session['email'])

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


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

            # TODO: Logout / disconnect does not work correctly unless the browser is closed / the cookie is no longer valid
            # at the moment it will show as failed to revoke token with a status 400 from google
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data.decode("utf-8") # .decode("utf-8") added by soeren
    print("access token: %s" % access_token)
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        FACEBOOK_APP_ID, FACEBOOK_SECRET_KEY, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1].decode("utf-8") # .decode("utf-8") added by soeren

    print("Exchange token result: %s" % result)
    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    print("url sent for API access:%s"% url)
    print("API JSON result: %s" % result)
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        print("You have successfully been logged out.")
        return redirect('/')
    else:
        print("You were not logged in")
        return redirect('/')


@app.route('/')
def showHome():
    return render_template("index.html")


@app.route('/meals')
def showMeals():
    meals = session.query(Meal).outerjoin(Meal.user)
    #user = getUserInfo(login_session['user_id'])
    return render_template("meals.html",meals=meals,getIngredients=getIngredients,loginSession=login_session)


@app.route('/food_facts')
def showFoodFacts():
    return render_template("food_facts.html")


@app.route('/meals/add', methods=['GET','POST'])
def addMeals():

    #del login_session['username']

    # required if no user has yet loged in so the dictionary does not have the key
    if 'username' not in login_session:
        return redirect ('/login')
        # TODO: return to the intendet page after login or redirect to original URL using request.referrer


    if request.method == 'POST' and request.form['button'] == "Save":

        # ---- FILE HANDLING -----
        filename = ""
        if 'file' not in request.files:
            print("file not in request.files")
            # TODO: Implement flash messages
            # flash('No file part')

            return redirect(request.url)

        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            # TODO: Implement flash
            # flash('No selected file')
            print("Filename == ''")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            now = datetime.now()
            filename = "%s.%s" % (now.strftime("%Y-%m-%d-%H-%M-%S-%f"), filename.rsplit('.', 1)[1])  #$s replaced by timestamp and file extension
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], "%s.%s" % (now.strftime("%Y-%m-%d-%H-%M-%S-%f"), file.filename.rsplit('.', 1)[1]))
            print("filename = " + filename)
            file.save(filepath)

        # ---- MEAL CREATION -----
        newMeal = Meal(title=request.form['title'],
                       description=request.form['description'],
                       portions=request.form['portions'],
                       calories="410 - 780",
                       image=filename,
                       user_id=login_session['user_id'])
        session.add(newMeal)
        session.commit()

        #---- INGREDIENTS CREATION ----



        # TODO: Optimize the creation of food and ingredient objects
        #      by avoiding too many commits

        x = 1
        while request.form['ingredient'+str(x)]:
            row = str(x)
            ingredient_text = request.form['ingredient'+row]

            # Translate local language to EN
            translation =  translate_client.translate(ingredient_text)
            print("newIngredient.titleEN = " + translation['translatedText'])
            print("detected source language = " + translation['detectedSourceLanguage'])

            # Identify food entity from entered text using language processing
            # use en language to improve results since en splits combined german words
            food_entity = analyze_ingredient(translation['translatedText'], language='en')
            print("Food entity: %s" % food_entity)

            # Query a food database (e.g. NDB) to retrieve nutrient information
            # and to create a food master data record. The id of such a record
            # is returned if a match in the food database was found.
            foodID = getFood(translation['translatedText'])
            if not foodID:
                foodID = None

            # Add new ingredient into database
            newIngredient = Ingredient(quantity=request.form['quantity'+row],
                                       uom_id=request.form['uom'+row],
                                       meal_id=newMeal.id,
                                       title=request.form['ingredient'+row],
                                       titleEN=translation['translatedText'],
                                       base_food_part=food_entity,
                                       food_id=foodID)

            session.add(newIngredient)
            session.commit()

            x += 1

        return redirect(url_for("showMeals"))

    elif request.method == 'POST' and request.form['button'] == "Cancel":
        print("POST button = Cancel")
        meals = session.query(Meal)
        return render_template("meals.html",meals=meals,getIngredients=getIngredients)
    else:  # 'GET':
        print("GET")
        uoms = session.query(UOM)
        foods = session.query(Food)
        return render_template("meals_add.html",uoms=uoms,foods=foods)


@app.route('/meals/delete/<int:meal_id>', methods=['GET','POST'])
def deleteMeal(meal_id):

    if 'username' not in login_session:
        return redirect ('/login')
        # TODO: return to the intendet page after login or redirect to original URL using request.referrer

    o = session.query(Meal).filter_by(id=meal_id).one()
    if request.method == 'POST' and request.form['button'] == "Delete":
        session.delete(o)
        session.commit()
        #TODO: flash("Meal deleted")
        #TODO: Delete image file from folder
        return redirect(url_for('showMeals'))
    elif request.method == 'GET':
        return render_template("meals_delete.html",meal=o)
    else:
        return redirect(url_for("showMeals"))


@app.route('/meals/view/<int:meal_id>')
def showMeal(meal_id):
    o = session.query(Meal).filter_by(id=meal_id).one()
    return render_template("meal_view.html",meal=o,getIngredients=getIngredients)


# API endpoint
@app.route('/meals/JSON')
def jsonMeals():
    items = session.query(Meal).all()
    return jsonify(Meals=[m.serialize for m in items])

# ---------------- User Helper Functions ---------------------------
# Creates a new user in the database
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

# Retrieves the user object
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

# Retrieves the user id based on an email
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Food database helper functions
def getFood(keyword):
    # Account Email: mailboxsoeren@gmail.com
    # Account ID: 738eae59-c15d-4b89-a621-bcd7182a51e2

    if NDB_KEY:
        n = ndb.NDB(NDB_KEY)
        results = n.search_keyword(keyword)
        if results:

            i = list(results['items'])[0] #TODO: identify relevant item, for now take the first one
            print("Found NDB item: "+i.get_name())

            # Create Food Main Group
            foodMainGroup = session.query(FoodMainGroup).filter_by(titleEN=i.get_group()).first()
            if not foodMainGroup:
                #print("Create new group: "+i.get_group())
                foodMainGroup = FoodMainGroup(titleEN=i.get_group())
                session.add(foodMainGroup)
                session.commit()

            # Create Food
            food = session.query(Food).filter_by(titleEN=i.get_name()).first()
            if not food:
                #print("Create new food: "+i.get_name())
                food = Food(titleEN=i.get_name(),ndb_code=i.get_ndbno(),food_maingroup_id=foodMainGroup.id)
                session.add(food)
                session.commit()

                # Create Nutrients
                report = n.food_report(i.get_ndbno())
                #print(report)

                nutrients = report['food'].get_nutrients()
                for n in nutrients:
                    # use existing nutrient object if exists
                    if n.get_name() in nutrientDict:
                        nutriendID = nutrientDict[n.get_name()] # retreive internal id based on the titleEN
                    # create new nutrient object
                    else:
                        #print("Create new nutrient: "+n.get_name())
                        translated_text = translate_client.translate(n.get_name(),
                                                                    target_language='de')['translatedText']
                        newNutrient = Nutrient(value_uom=n.get_unit(),
                                            titleEN=n.get_name(),
                                            titleDE=translated_text)
                        session.add(newNutrient)
                        session.commit()
                        nutriendID = newNutrient.id

                        # TODO: all get into unknown atm
                    #print(n.get_unit())
                    if n.get_unit() in uomDict:
                        uomID = n.get_unit()
                    else:
                        print("unknown unit of measure")
                        uomID = "x" #TODO: improve later

                    #print("Create new food composition")
                    fc = FoodComposition(food_id=food.id,
                                        nutrient_id=nutriendID,
                                        per_qty_uom=uomID,
                                        per_qty=100,
                                        value=n.get_value())
                    session.add(fc)
                    session.commit()
            return food.id
        else:
            print("No results in NDB found")
            return None
    else:
        print("Missing API Key in Environment Variable")
        return None


def analyze_ingredient(ingredient_text, **kwargs):

    target_language = kwargs['language']

    # Create a whole sentence so the language api understands the context
    # and provides better results
    intro_text = {
        'de':'Die Speise besteht aus',
        'en':'The meal consists of'
        }

    # Using google language api to identify
    # adjectives = processing (pre or at home)
    # nouns = custom UOM and ingredients/food
    # conjunctions = "and", "or", etc. for alternatives
    # Reference: https://cloud.google.com/natural-language/docs/reference/rest/v1/Token
    content = ' '.join([intro_text[target_language],ingredient_text])
    print("content: %s" % content)
    document = language.types.Document(
        content=content,
        type=language.enums.Document.Type.PLAIN_TEXT,
        language=target_language)
    response = language_client.analyze_syntax(
        document=document,
        encoding_type='UTF32')
    tokens = response.tokens

    # part-of-speech tags from enums.PartOfSpeech.Tag
    # reference: https://cloud.google.com/natural-language/docs/reference/rest/v1/Token#partofspeech
    pos_tag = ('UNKNOWN', 'ADJ', 'ADP', 'ADV', 'CONJ', 'DET', 'NOUN', 'NUM',
           'PRON', 'PRT', 'PUNCT', 'VERB', 'X', 'AFFIX')

    counter = 0
    skip_intro_words = 4
    for token in tokens:
        counter += 1
        print(u'{}: {}'.format(pos_tag[token.part_of_speech.tag],token.text.content))
        # TODO: Handle multiple nouns
        # for example 'clove of garlic' should return garlic and not clove
        # wheat flour should return wheat flour
        # noun + "of" could be understood as a component of the whole as custom uom
        if (counter > skip_intro_words) and (pos_tag[token.part_of_speech.tag] == 'NOUN'):
            return token.lemma  # lemma is the word stem of the word
    return None

def getIngredients(meal_id):
    if meal_id:
        items = session.query(Ingredient).filter_by(meal_id=meal_id)
        return items
    else:
        return false


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get('PORT', 8000))
    app.run(host='', port=port)
