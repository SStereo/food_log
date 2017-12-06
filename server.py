import os  # required to have access to the Port environment variable
from flask import Flask, render_template, request, url_for, redirect, flash, jsonify
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

UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.secret_key = "ABC123"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#engine = create_engine('postgresql://vagrant:vagrant@127.0.0.1:5432/np')
engine = create_engine('postgres://njxqkgsvotldpo:0091ec1051866196d42e608aadc421ef9bb58c37d9fcfe0e7bac4e9ce63929f8@ec2-54-228-182-57.eu-west-1.compute.amazonaws.com:5432/ddjblvctcusagj')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
def ShowWelcome():
    return render_template("index.html")


@app.route('/meals')
def showMeals():
    meals = session.query(Meal)
    return render_template("meals.html",meals=meals,getIngredients=getIngredients)


@app.route('/meals/add', methods=['GET','POST'])
def addMeals():
    if request.method == 'POST':
        # ---- IMAGE UPLOAD HANDLER -----
        if 'file' not in request.files:

            # TODO: Implement flash messages
            # flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            # TODO: Implement flash
            # flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # ---- FORM DATA HANDLER -----
        


    if request.method == 'GET':
        uoms = session.query(UOM)
        foods = session.query(Food)
        return render_template("meals_add.html",uoms=uoms,foods=foods)


def getIngredients(meal_id):
    items = session.query(Ingredient).filter_by(meal_id=meal_id)
    return items


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get('PORT', 8000))
    app.run(host='', port=port)
