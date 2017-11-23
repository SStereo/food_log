from np_db import (Base,
                   UOM,
                   Meal,
                   Ingredient,
                   Food,
                   FoodComposition,
                   Nutrient,
                   ShoppingListItem)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine('postgresql://vagrant:vagrant@127.0.0.1:5432/np')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

print("------ Meals ------")
for instance in session.query(Meal).\
             filter(Meal.title.like('%Dhal%')):
    meal_id = instance.id
    print(instance.id, instance.title, instance.portions)
print("------ Ingredients ------")
for instance in session.query(Ingredient).filter(Ingredient.meal_id==meal_id):
    print(instance.quantity, instance.uom.uom, instance.food.title)
