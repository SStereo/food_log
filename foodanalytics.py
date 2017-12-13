import ndb
from googletrans import Translator

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

#engine = create_engine('postgresql://vagrant:vagrant@127.0.0.1:5432/np')
engine = create_engine('postgres://njxqkgsvotldpo:0091ec1051866196d42e608aadc421ef9bb58c37d9fcfe0e7bac4e9ce63929f8@ec2-54-228-182-57.eu-west-1.compute.amazonaws.com:5432/ddjblvctcusagj')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def translateFoodtoEN(food_id):

# check if food item has already an english translation stored in the db

# detect Language

# if language not EN then translateFood

# Store translated title in food table


def analyzeFood(food_id):

# identify processing, preparation other terms in food titleEN


def MapFoodToReference(food_id):

# Identify if Reference Food exists if not create a new entry

# Reference the food reference object


def getFoodNutrients(food_id):

# check if nutrient data exists or not

# call NDB method to retrieve nutrient information

# store base unit of measure for nutrient values (e.g. 100g)

# store base nutrients as kilojoule, Carbonhydrates, fat, protein

# create nutrient records
