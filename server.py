from flask import Flask, render_template, request, url_for, redirect, flash, jsonify
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

app = Flask(__name__)
app.secret_key = "ABC123"

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


def getIngredients(meal_id):
    items = session.query(Ingredient).filter_by(meal_id=meal_id)
    return items

if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=8080)
