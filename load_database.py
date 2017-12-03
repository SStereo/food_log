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
           UOM(uom="g",title="gram"),
           UOM(uom="kg",title="kilogram"),
           UOM(uom="l",title="liter"),
           UOM(uom="ml",title="milliliter"),
           UOM(uom="tbsp",title="tablespoon"),
           UOM(uom="tsp",title="teaspoon"),
           UOM(uom="pn",title="pinch"),
           UOM(uom="cup",title="cup"),
           UOM(uom="oz",title="shot"),
           UOM(uom="pc",title="piece")
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
           Food(title="Wasser"),
           Food(title="Stange Lauch"),
           Food(title="Karotte"),
           Food(title="Knollensellerie, mittelgroß"),
           Food(title="Linsen"),
           Food(title="Räucherbauch"),
           Food(title="Gemüsebrühe"),
           Food(title="Kartoffel"),
           Food(title="Wienerle"),
           Food(title="Öl"),
           Food(title="Muskat"),
           Food(title="Rotweinessig"),
           Food(title="Spätzle"),
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
                      food=obj_foods[0]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[4],
                      meal=obj_meals[0],
                      food=obj_foods[1]
                      ),
           Ingredient(quantity=100,
                      uom=obj_uoms[0],
                      meal=obj_meals[0],
                      food=obj_foods[2]
                      ),
           Ingredient(quantity=200,
                      uom=obj_uoms[3],
                      meal=obj_meals[0],
                      food=obj_foods[3]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[4],
                      meal=obj_meals[0],
                      food=obj_foods[4]
                      ),
           Ingredient(quantity=400,
                      uom=obj_uoms[0],
                      meal=obj_meals[0],
                      food=obj_foods[5]
                      ),
           Ingredient(quantity=2,
                      uom=obj_uoms[7],
                      meal=obj_meals[0],
                      food=obj_foods[6]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[7],
                      meal=obj_meals[0],
                      food=obj_foods[7]
                      ),
           Ingredient(quantity=2,
                      uom=obj_uoms[4],
                      meal=obj_meals[0],
                      food=obj_foods[8]
                      ),
           Ingredient(quantity=5,
                      uom=obj_uoms[4],
                      meal=obj_meals[0],
                      food=obj_foods[9]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[9],
                      meal=obj_meals[0],
                      food=obj_foods[10]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[4],
                      meal=obj_meals[0],
                      food=obj_foods[11]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[6],
                      meal=obj_meals[0],
                      food=obj_foods[12]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[6],
                      meal=obj_meals[0],
                      food=obj_foods[13]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[5],
                      meal=obj_meals[0],
                      food=obj_foods[14]
                      ),
           Ingredient(quantity=200,
                      uom=obj_uoms[3],
                      meal=obj_meals[0],
                      food=obj_foods[15]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[9],
                      meal=obj_meals[1],
                      food=obj_foods[0]
                      ),
           Ingredient(quantity=0.5,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      food=obj_foods[16]
                      ),
           Ingredient(quantity=50,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      food=obj_foods[17]
                      ),
           Ingredient(quantity=50,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      food=obj_foods[18]
                      ),
           Ingredient(quantity=50,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      food=obj_foods[19]
                      ),
           Ingredient(quantity=50,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      food=obj_foods[20]
                      ),
           Ingredient(quantity=50,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      food=obj_foods[21]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      food=obj_foods[22]
                      ),
           Ingredient(quantity=4,
                      uom=obj_uoms[9],
                      meal=obj_meals[1],
                      food=obj_foods[23]
                      ),
           Ingredient(quantity=2,
                      uom=obj_uoms[4],
                      meal=obj_meals[1],
                      food=obj_foods[24]
                      ),
           Ingredient(quantity=2,
                      uom=obj_uoms[4],
                      meal=obj_meals[1],
                      food=obj_foods[12]
                      ),
           Ingredient(quantity=2,
                      uom=obj_uoms[4],
                      meal=obj_meals[1],
                      food=obj_foods[13]
                      ),
           Ingredient(quantity=2,
                      uom=obj_uoms[4],
                      meal=obj_meals[1],
                      food=obj_foods[25]
                      ),
           Ingredient(quantity=250,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      food=obj_foods[26]
                      ),
]

session.add_all(obj_uoms)
session.add_all(obj_foods)
session.add_all(obj_meals)
session.add_all(obj_ingredients)
session.commit()
