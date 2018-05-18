

from huntingfood.models import User, UserGroup, UOM, Meal, Ingredient, Material, MaterialForecast
from huntingfood.models import FoodComposition, Nutrient, ShoppingOrder
from huntingfood.models import ShoppingOrderItem, FoodMainGroup
from huntingfood.models import InventoryItem, Inventory, DietPlan, DietPlanItem
from huntingfood.models import TradeItem, Place

from huntingfood import db

# Deletes existing records in the tables

num_rows_deleted = User.query.delete()
db.session.commit()

num_rows_deleted = Ingredient.query.delete()
db.session.commit()

num_rows_deleted = FoodComposition.query.delete()
db.session.commit()

num_rows_deleted = Nutrient.query.delete()
db.session.commit()

num_rows_deleted = DietPlanItem.query.delete()
db.session.commit()

num_rows_deleted = DietPlan.query.delete()
db.session.commit()

num_rows_deleted = MaterialForecast.query.delete()
db.session.commit()

num_rows_deleted = InventoryItem.query.delete()
db.session.commit()

num_rows_deleted = Inventory.query.delete()
db.session.commit()

num_rows_deleted = Material.query.delete()
db.session.commit()

num_rows_deleted = Meal.query.delete()
db.session.commit()

num_rows_deleted = UOM.query.delete()
db.session.commit()



# Create default user

obj_users = [
            User(
                name="admin",
                email="admin@huntingfood.com",
                language="DE")
]


# Create UOM objects
# See: https://www.asknumbers.com/CookingConversion.aspx

obj_uoms = [
           UOM(uom="g",longEN="gram",shortDE="g",type="2"),
           UOM(uom="mg",longEN="milligram",shortDE="mg",type="3"),
           UOM(uom="µg",longEN="micrograms",shortDE="µg",type="3"),
           UOM(uom="IU",longEN="international unit",shortDE="IE",type="3"),
           UOM(uom="kg",longEN="kilogram",shortDE="kg",type="1"),
           UOM(uom="l",longEN="liter",shortDE="l",type="1"),
           UOM(uom="ml",longEN="milliliter",shortDE="ml",type="1"),
           UOM(uom="tbsp",longEN="tablespoon",shortDE="El",type="1"),
           UOM(uom="tsp",longEN="teaspoon",shortDE="Tl",type="1"),
           UOM(uom="pn",longEN="pinch",shortDE="Prise",type="1"),
           UOM(uom="cup",longEN="cup",shortDE="Tasse",type="1"),
           UOM(uom="oz",longEN="shot",shortDE="Unze",type="1"),
           UOM(uom="pc",longEN="piece",shortDE="St",type="1"),
           UOM(uom="kcal",longEN="kilocalories",shortDE="kcal",type="3"),
           UOM(uom="x",longEN="unknown",shortDE="x",type="3")
]


# TODO: change field to say ndb nutrient mapping or so because other database have other terms for lookup
obj_nutrients = [
           Nutrient(value_uom="g",titleEN="Water",titleDE="Wasser"),
           Nutrient(value_uom="kcal",titleEN="Energy",titleDE="Energie"),
           Nutrient(value_uom="g",titleEN="Protein",titleDE="Eiweis"),
           Nutrient(value_uom="g",titleEN="Total lipid (fat)",titleDE="Fett"),
           Nutrient(value_uom="g",titleEN="Carbohydrate, by difference",titleDE="Kohlenhydrate"),
           Nutrient(value_uom="g",titleEN="Fiber, total dietary",titleDE="Ballaststoff"),
           Nutrient(value_uom="g",titleEN="Sugars, total",titleDE="Zucker"),
           Nutrient(value_uom="mg",titleEN="Calcium, Ca",titleDE="Kalzium"),
           Nutrient(value_uom="mg",titleEN="Iron, Fe",titleDE="Eisen"),
           Nutrient(value_uom="mg",titleEN="Magnesium, Mg",titleDE="Magnesium"),
           Nutrient(value_uom="mg",titleEN="Phosphorus, P",titleDE="Phosphor"),
           Nutrient(value_uom="mg",titleEN="Potassium, K",titleDE="Potassium"),
           Nutrient(value_uom="mg",titleEN="Sodium, Na",titleDE="Sodium"),
           Nutrient(value_uom="mg",titleEN="Zinc, Zn",titleDE="Zink"),
           Nutrient(value_uom="mg",titleEN="Vitamin C, total ascorbic acid",titleDE="Vitamin C"),
           Nutrient(value_uom="mg",titleEN="Thiamin",titleDE="Thiamin"),
           Nutrient(value_uom="mg",titleEN="Riboflavin",titleDE="Riboflavin"),
           Nutrient(value_uom="mg",titleEN="Vitamin B-6",titleDE="Vitamin B-6"),
           Nutrient(value_uom="µg",titleEN="Folate, DFE",titleDE="Folsäure"),
           Nutrient(value_uom="µg",titleEN="Vitamin B-12",titleDE="Vitamin B-12"),
           Nutrient(value_uom="µg",titleEN="Vitamin A, RAE",titleDE="Vitamin A, RAE"),
           Nutrient(value_uom="IU",titleEN="Vitamin A, IU",titleDE="Vitamin A, IU"),
           Nutrient(value_uom="mg",titleEN="Vitamin E (alpha-tocopherol)",titleDE="Vitamin E"),
           Nutrient(value_uom="µg",titleEN="Vitamin D (D2 + D3)",titleDE="Vitamin D (D2 + D3)"),
           Nutrient(value_uom="IU",titleEN="Vitamin D",titleDE="Vitamin D"),
           Nutrient(value_uom="µg",titleEN="Vitamin K (phylloquinone)",titleDE="Vitamin K"),
           Nutrient(value_uom="g",titleEN="Fatty acids, total saturated",titleDE="gesättigte Fettsäuren"),
           Nutrient(value_uom="g",titleEN="Fatty acids, total monounsaturated",titleDE="einfach ungesättigte Fettsäure"),
           Nutrient(value_uom="g",titleEN="Fatty acids, total polyunsaturated",titleDE="mehrfach ungesättigte Fettsäure"),
           Nutrient(value_uom="g",titleEN="Fatty acids, total trans",titleDE="trans-Fettsäuren"),
           Nutrient(value_uom="mg",titleEN="Cholesterol",titleDE="Cholesterin"),
           Nutrient(value_uom="mg",titleEN="Caffeine",titleDE="Koffein")
]

obj_foods = [
           Material(titleDE="Zwiebel"),
           Material(titleDE="Curry"),
           Material(titleDE="rote Linsen"),
           Material(titleDE="Gemüsebrühe"),
           Material(titleDE="Tomatenmark"),
           Material(titleDE="gehackte Tomaten"),
           Material(titleDE="Blumenkohl"),
           Material(titleDE="grüne Bohnen"),
           Material(titleDE="frischer Koriander"),
           Material(titleDE="griechischer Joghurt"),
           Material(titleDE="Knoblauchzehe"),
           Material(titleDE="Olivenöl"),
           Material(titleDE="Salz"),
           Material(titleDE="schwarzer Pfeffer"),
           Material(titleDE="Zucker"),
           Material(titleDE="Wasser"),
           Material(titleDE="Stange Lauch"),
           Material(titleDE="Karotte"),
           Material(titleDE="Knollensellerie, mittelgroß"),
           Material(titleDE="Linsen"),
           Material(titleDE="Räucherbauch"),
           Material(titleDE="Kartoffel"),
           Material(titleDE="Wienerle"),
           Material(titleDE="Öl"),
           Material(titleDE="Muskat"),
           Material(titleDE="Rotweinessig"),
           Material(titleDE="Spätzle"),
]

obj_meals = [
           Meal(title="Linsen-Dhal",
                description="""\
                Dieses Dal ist ein indisches Rotes Linsen-Gericht und kommt
                schön würzig mit Ingwer- und Gewürzaromen daher.\
                """,
                portions=2,
                rating=5,
                image="linsendhal.jpg",
                owner=obj_users[0]
                ),
            Meal(title="Linsen mit Spätzle und Saitenwürstchen",
                 description="""\
                 Leckers schwäbisches Gericht.\
                 """,
                 portions=2,
                 rating=5,
                 image="linsenmitspaetzle.jpg",
                 owner=obj_users[0]
                 ),
            Meal(title="Geschmelzte Maultaschen",
                 description="""\
                 Leckers schwäbisches Gericht.\
                 """,
                 portions=2,
                 rating=5,
                 image="geschmelztemaultaschen.jpg",
                 owner=obj_users[0]
                 )
]

obj_ingredients = [
           Ingredient(quantity=50,
                      uom=obj_uoms[0],
                      meal=obj_meals[0],
                      title="Zwiebel",
                      material=obj_foods[0]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[4],
                      meal=obj_meals[0],
                      title="Curry",
                      material=obj_foods[1]
                      ),
           Ingredient(quantity=100,
                      uom=obj_uoms[0],
                      meal=obj_meals[0],
                      title="rote Linsen",
                      material=obj_foods[2]
                      ),
           Ingredient(quantity=200,
                      uom=obj_uoms[3],
                      meal=obj_meals[0],
                      title="Gemüsebrühe",
                      material=obj_foods[3]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[4],
                      meal=obj_meals[0],
                      title="Tomatenmark",
                      material=obj_foods[4]
                      ),
           Ingredient(quantity=400,
                      uom=obj_uoms[0],
                      meal=obj_meals[0],
                      title="gehackte Tomaten",
                      material=obj_foods[5]
                      ),
           Ingredient(quantity=2,
                      uom=obj_uoms[7],
                      meal=obj_meals[0],
                      title="Blumenkohl",
                      material=obj_foods[6]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[7],
                      meal=obj_meals[0],
                      title="grüne Bohnen",
                      material=obj_foods[7]
                      ),
           Ingredient(quantity=2,
                      uom=obj_uoms[4],
                      meal=obj_meals[0],
                      title="frischer Koriander",
                      material=obj_foods[8]
                      ),
           Ingredient(quantity=5,
                      uom=obj_uoms[4],
                      meal=obj_meals[0],
                      title="griechischer Joghurt",
                      material=obj_foods[9]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[9],
                      meal=obj_meals[0],
                      title="Knoblauchzehe",
                      material=obj_foods[10]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[4],
                      meal=obj_meals[0],
                      title="Olivenöl",
                      material=obj_foods[11]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[6],
                      meal=obj_meals[0],
                      title="Salz",
                      material=obj_foods[12]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[6],
                      meal=obj_meals[0],
                      title="schwarzer Pfeffer",
                      material=obj_foods[13]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[5],
                      meal=obj_meals[0],
                      title="Zucker",
                      material=obj_foods[14]
                      ),
           Ingredient(quantity=200,
                      uom=obj_uoms[3],
                      meal=obj_meals[0],
                      title="Wasser",
                      material=obj_foods[15]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[9],
                      meal=obj_meals[1],
                      title="Zwiebel",
                      material=obj_foods[0]
                      ),
           Ingredient(quantity=0.5,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      title="Stange Lauch",
                      material=obj_foods[16]
                      ),
           Ingredient(quantity=50,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      title="Karotte",
                      material=obj_foods[17]
                      ),
           Ingredient(quantity=50,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      title="Knollensellerie, mittelgroß",
                      material=obj_foods[18]
                      ),
           Ingredient(quantity=50,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      title="Linsen",
                      material=obj_foods[19]
                      ),
           Ingredient(quantity=50,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      title="Räucherbauch",
                      material=obj_foods[20]
                      ),
           Ingredient(quantity=50,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      title="Gemüsebrühe",
                      material=obj_foods[3]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      title="Kartoffel",
                      material=obj_foods[21]
                      ),
           Ingredient(quantity=4,
                      uom=obj_uoms[9],
                      meal=obj_meals[1],
                      title="Wienerle",
                      material=obj_foods[22]
                      ),
           Ingredient(quantity=2,
                      uom=obj_uoms[4],
                      meal=obj_meals[1],
                      title="Öl",
                      material=obj_foods[23]
                      ),
           Ingredient(quantity=2,
                      uom=obj_uoms[4],
                      meal=obj_meals[1],
                      title="Salz",
                      material=obj_foods[12]
                      ),
           Ingredient(quantity=2,
                      uom=obj_uoms[4],
                      meal=obj_meals[1],
                      title="schwarzer Pfeffer",
                      material=obj_foods[13]
                      ),
           Ingredient(quantity=2,
                      uom=obj_uoms[4],
                      meal=obj_meals[1],
                      title="Rotweinessig",
                      material=obj_foods[24]
                      ),
           Ingredient(quantity=250,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      title="Spätzle",
                      material=obj_foods[25]
                      ),
]


obj_places = [
    Place(
        titleEN='NORMA Frauenaurach',
        titleDE='NORMA Frauenaurach',
        google_place_id='ChIJe5c7N0H_oUcRg62tY-FBrVA',
        geo_lat='49.561972',
        geo_lng='10.961898',
        ),
    Place(
        titleEN='Dorfladen Hüttendorf',
        titleDE='Dorfladen Hüttendorf',
        google_place_id='ChIJn3nyUHL_oUcRR_VbmRcwF-w',
        geo_lat='49.548049',
        geo_lng='10.961172',
        ),
    Place(
        titleEN='Edeka Neumühle',
        titleDE='Edeka Neumühle',
        google_place_id='ChIJ4-bDBrf4oUcRYofAX6KmRUU',
        geo_lat='49.588103',
        geo_lng='10.977139',
        )
            ]


db.session.add_all(obj_users)
db.session.add_all(obj_uoms)
db.session.add_all(obj_nutrients)
db.session.add_all(obj_foods)
db.session.add_all(obj_meals)
db.session.add_all(obj_ingredients)
db.session.add_all(obj_places)
db.session.commit()
