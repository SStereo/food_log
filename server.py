import os  # required to have access to the Port environment variable
import json
from google.oauth2 import service_account
from google.cloud import translate
from oauth2client.client import GoogleCredentials #for google cloud authentication

from datetime import datetime  #required for method "now" for file name change
from flask import Flask, render_template, request, url_for, redirect, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename  #required for file upload
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from food_database import (Base,
                   UOM,
                   Meal,
                   Ingredient,
                   Food,
                   FoodComposition,
                   Nutrient,
                   ShoppingListItem)

UPLOAD_FOLDER = 'upload'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.secret_key = "ABC123"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#app.add_url_rule('/uploads/<path:filename>', endpoint='uploads',
                 #view_func=app.send_static_file)

#engine = create_engine('postgresql://vagrant:vagrant@127.0.0.1:5432/np')
engine = create_engine('postgres://njxqkgsvotldpo:0091ec1051866196d42e608aadc421ef9bb58c37d9fcfe0e7bac4e9ce63929f8@ec2-54-228-182-57.eu-west-1.compute.amazonaws.com:5432/ddjblvctcusagj')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


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
@app.route('/')
def showHome():
    return render_template("index.html")


@app.route('/meals')
def showMeals():
    meals = session.query(Meal)
    return render_template("meals.html",meals=meals,getIngredients=getIngredients)


@app.route('/meals/add', methods=['GET','POST'])
def addMeals():
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
                       image=filename)
        session.add(newMeal)
        session.commit()

        #---- INGREDIENTS CREATION ----

        PK = os.environ.get('GOOGLE_CLOUD_CREDENTIALS_PK')

        #jsonString = json.dumps(d)

        jsonString = """{
          "type": "service_account",
          "project_id": "long-memory-188919",
          "private_key_id": "b26b39e14a2375751b5064b77e426243b4625de4",
          "private_key": \""""+PK+"""",
          "client_email": "serviceaccount-owner@long-memory-188919.iam.gserviceaccount.com",
          "client_id": "106478515271128625146",
          "auth_uri": "https://accounts.google.com/o/oauth2/auth",
          "token_uri": "https://accounts.google.com/o/oauth2/token",
          "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
          "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/serviceaccount-owner%40long-memory-188919.iam.gserviceaccount.com"
        }"""

        service_account_info = json.loads(jsonString)
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info)

        #client = Client(credentials=credentials)
        client = translate.Client(target_language='en',credentials=credentials)

        # TODO: Optimize the creation of food and ingredient objects
        #      by avoiding too many commits

        x = 1
        while request.form['ingredient'+str(x)]:
            row = str(x)

            #TODO: add new logic to determine Food
            #newFood = session.query(Food).filter_by(title=request.form['ingredient'+row]).first()
            #if not newFood:
            #    newFood = Food(title=request.form['ingredient'+row])
            #    session.add(newFood)
            #    session.commit()

            translation =  client.translate(request.form['ingredient'+row])['translatedText']

            newIngredient = Ingredient(quantity=request.form['quantity'+row],
                                       uom_id=request.form['uom'+row],
                                       meal_id=newMeal.id,
                                       title=request.form['ingredient'+row],
                                       titleEN=translation)

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
