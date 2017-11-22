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

# Create UOM objects
# See: https://www.asknumbers.com/CookingConversion.aspx

obj_uoms = [
           UOM(uom="g",title="gram"),
           UOM(uom="kg",title="kilogram"),
           UOM(uom="l",title="liter"),
           UOM(uom="ml",title="milliliter"),
           UOM(uom="tbsp",title="tablespoon"),
           UOM(uom="tsp",title="teaspoon"),
           UOM(uom="pn",title="pinch"),
           UOM(uom="cup",title="cup"),
           UOM(uom="oz",title="shot")
]

obj_foods = [
           Food(title="Zwiebel"),
           Food(title="Curry"),
           Food(title="rote Linsen"),
           Food(title="Gemüsebrühe"),
           Food(title="Tomatenmark"),
           Food(title="gehackte Tomaten"),
           Food(title="Blumenkohl"),
           Food(title="grüne Bohnen"),
           Food(title="frischer Koriander"),
           Food(title="griechischer Joghurt"),
           Food(title="Knoblauchzehe"),
           Food(title="Olivenöl"),
           Food(title="Salz"),
           Food(title="schwarzer Pfeffer"),
           Food(title="Zucker"),
           Food(title="Wasser")
]

obj_meals = [
           Meal(title="Linsen-Dhal",
                description="""\
                Dieses Dal ist ein indisches Rotes Linsen-Gericht und kommt
                schön würzig mit Ingwer- und Gewürzaromen daher.\
                """,
                portions=2,
                rating=5,
                )
]

obj_ingredients = [
           Ingredient(quantity=50,
                      uom=obj_uoms[0],
                      meal=obj_meals[0],
                      food=obj_foods[0]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[4],
                      meal=obj_meals[0],
                      food=obj_foods[1]
                      )
]

session.add_all(obj_uoms)
session.add_all(obj_foods)
session.add_all(obj_meals)
session.add_all(obj_ingredients)
session.commit()
