from food_database import (Base,
                   UOM,
                   Meal,
                   Ingredient,
                   Food,
                   FoodComposition,
                   Nutrient,
                   ShoppingListItem)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


#engine = create_engine('postgresql://vagrant:vagrant@127.0.0.1:5432/np')
engine = create_engine('postgres://njxqkgsvotldpo:0091ec1051866196d42e608aadc421ef9bb58c37d9fcfe0e7bac4e9ce63929f8@ec2-54-228-182-57.eu-west-1.compute.amazonaws.com:5432/ddjblvctcusagj')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Deletes existing records in the tables
num_rows_deleted = session.query(Ingredient).delete()
session.commit()

num_rows_deleted = session.query(Food).delete()
session.commit()

num_rows_deleted = session.query(Meal).delete()
session.commit()

num_rows_deleted = session.query(UOM).delete()
session.commit()


# Create UOM objects
# See: https://www.asknumbers.com/CookingConversion.aspx

obj_uoms = [
           UOM(uom="g",longEN="gram",shortDE="g"),
           UOM(uom="kg",longEN="kilogram",shortDE="kg"),
           UOM(uom="l",longEN="liter",shortDE="l"),
           UOM(uom="ml",longEN="milliliter",shortDE="ml"),
           UOM(uom="tbsp",longEN="tablespoon",shortDE="El"),
           UOM(uom="tsp",longEN="teaspoon",shortDE="Tl"),
           UOM(uom="pn",longEN="pinch",shortDE="Prise"),
           UOM(uom="cup",longEN="cup",shortDE="Tasse"),
           UOM(uom="oz",longEN="shot",shortDE="Unze"),
           UOM(uom="pc",longEN="piece",shortDE="")
]

obj_foods = [
           Food(titleDE="Zwiebel"),
           Food(titleDE="Curry"),
           Food(titleDE="rote Linsen"),
           Food(titleDE="Gemüsebrühe"),
           Food(titleDE="Tomatenmark"),
           Food(titleDE="gehackte Tomaten"),
           Food(titleDE="Blumenkohl"),
           Food(titleDE="grüne Bohnen"),
           Food(titleDE="frischer Koriander"),
           Food(titleDE="griechischer Joghurt"),
           Food(titleDE="Knoblauchzehe"),
           Food(titleDE="Olivenöl"),
           Food(titleDE="Salz"),
           Food(titleDE="schwarzer Pfeffer"),
           Food(titleDE="Zucker"),
           Food(titleDE="Wasser"),
           Food(titleDE="Stange Lauch"),
           Food(titleDE="Karotte"),
           Food(titleDE="Knollensellerie, mittelgroß"),
           Food(titleDE="Linsen"),
           Food(titleDE="Räucherbauch"),
           Food(titleDE="Kartoffel"),
           Food(titleDE="Wienerle"),
           Food(titleDE="Öl"),
           Food(titleDE="Muskat"),
           Food(titleDE="Rotweinessig"),
           Food(titleDE="Spätzle"),
]

obj_meals = [
           Meal(title="Linsen-Dhal",
                description="""\
                Dieses Dal ist ein indisches Rotes Linsen-Gericht und kommt
                schön würzig mit Ingwer- und Gewürzaromen daher.\
                """,
                portions=2,
                rating=5,
                image="linsendhal.jpg"
                ),
            Meal(title="Linsen mit Spätzle und Saitenwürstchen",
                 description="""\
                 Leckers schwäbisches Gericht.\
                 """,
                 portions=2,
                 rating=5,
                 image="linsenmitspaetzle.jpg"
                 ),
            Meal(title="Geschmelzte Maultaschen",
                 description="""\
                 Leckers schwäbisches Gericht.\
                 """,
                 portions=2,
                 rating=5,
                 image="geschmelztemaultaschen.jpg"
                 )
]

obj_ingredients = [
           Ingredient(quantity=50,
                      uom=obj_uoms[0],
                      meal=obj_meals[0],
                      title="Zwiebel",
                      food=obj_foods[0]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[4],
                      meal=obj_meals[0],
                      title="Curry",
                      food=obj_foods[1]
                      ),
           Ingredient(quantity=100,
                      uom=obj_uoms[0],
                      meal=obj_meals[0],
                      title="rote Linsen",
                      food=obj_foods[2]
                      ),
           Ingredient(quantity=200,
                      uom=obj_uoms[3],
                      meal=obj_meals[0],
                      title="Gemüsebrühe",
                      food=obj_foods[3]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[4],
                      meal=obj_meals[0],
                      title="Tomatenmark",
                      food=obj_foods[4]
                      ),
           Ingredient(quantity=400,
                      uom=obj_uoms[0],
                      meal=obj_meals[0],
                      title="gehackte Tomaten",
                      food=obj_foods[5]
                      ),
           Ingredient(quantity=2,
                      uom=obj_uoms[7],
                      meal=obj_meals[0],
                      title="Blumenkohl",
                      food=obj_foods[6]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[7],
                      meal=obj_meals[0],
                      title="grüne Bohnen",
                      food=obj_foods[7]
                      ),
           Ingredient(quantity=2,
                      uom=obj_uoms[4],
                      meal=obj_meals[0],
                      title="frischer Koriander",
                      food=obj_foods[8]
                      ),
           Ingredient(quantity=5,
                      uom=obj_uoms[4],
                      meal=obj_meals[0],
                      title="griechischer Joghurt",
                      food=obj_foods[9]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[9],
                      meal=obj_meals[0],
                      title="Knoblauchzehe",
                      food=obj_foods[10]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[4],
                      meal=obj_meals[0],
                      title="Olivenöl",
                      food=obj_foods[11]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[6],
                      meal=obj_meals[0],
                      title="Salz",
                      food=obj_foods[12]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[6],
                      meal=obj_meals[0],
                      title="schwarzer Pfeffer",
                      food=obj_foods[13]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[5],
                      meal=obj_meals[0],
                      title="Zucker",
                      food=obj_foods[14]
                      ),
           Ingredient(quantity=200,
                      uom=obj_uoms[3],
                      meal=obj_meals[0],
                      title="Wasser",
                      food=obj_foods[15]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[9],
                      meal=obj_meals[1],
                      title="Zwiebel",
                      food=obj_foods[0]
                      ),
           Ingredient(quantity=0.5,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      title="Stange Lauch",
                      food=obj_foods[16]
                      ),
           Ingredient(quantity=50,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      title="Karotte",
                      food=obj_foods[17]
                      ),
           Ingredient(quantity=50,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      title="Knollensellerie, mittelgroß",
                      food=obj_foods[18]
                      ),
           Ingredient(quantity=50,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      title="Linsen",
                      food=obj_foods[19]
                      ),
           Ingredient(quantity=50,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      title="Räucherbauch",
                      food=obj_foods[20]
                      ),
           Ingredient(quantity=50,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      title="Gemüsebrühe",
                      food=obj_foods[3]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      title="Kartoffel",
                      food=obj_foods[21]
                      ),
           Ingredient(quantity=4,
                      uom=obj_uoms[9],
                      meal=obj_meals[1],
                      title="Wienerle",
                      food=obj_foods[22]
                      ),
           Ingredient(quantity=2,
                      uom=obj_uoms[4],
                      meal=obj_meals[1],
                      title="Öl",
                      food=obj_foods[23]
                      ),
           Ingredient(quantity=2,
                      uom=obj_uoms[4],
                      meal=obj_meals[1],
                      title="Salz",
                      food=obj_foods[12]
                      ),
           Ingredient(quantity=2,
                      uom=obj_uoms[4],
                      meal=obj_meals[1],
                      title="schwarzer Pfeffer",
                      food=obj_foods[13]
                      ),
           Ingredient(quantity=2,
                      uom=obj_uoms[4],
                      meal=obj_meals[1],
                      title="Rotweinessig",
                      food=obj_foods[24]
                      ),
           Ingredient(quantity=250,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      title="Spätzle",
                      food=obj_foods[25]
                      ),
]

session.add_all(obj_uoms)
session.add_all(obj_foods)
session.add_all(obj_meals)
session.add_all(obj_ingredients)
session.commit()
