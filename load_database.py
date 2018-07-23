from huntingfood.models import User, UserGroup, UOM, Meal, Ingredient, Material, MaterialForecast
from huntingfood.models import FoodComposition, Nutrient, ShoppingOrder
from huntingfood.models import ShoppingOrderItem, FoodMainGroup
from huntingfood.models import InventoryItem, Inventory, DietPlan, DietPlanItem, ConsumptionPlanItem, ConsumptionPlan
from huntingfood.models import TradeItem, Place, Country, State

from huntingfood import db

import json

# Deletes existing records in the tables

num_rows_deleted = User.query.delete()
db.session.commit()

num_rows_deleted = Ingredient.query.delete()
db.session.commit()

num_rows_deleted = FoodComposition.query.delete()
db.session.commit()

num_rows_deleted = Nutrient.query.delete()
db.session.commit()

num_rows_deleted = ConsumptionPlanItem.query.delete()
db.session.commit()

num_rows_deleted = ConsumptionPlan.query.delete()
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

num_rows_deleted = State.query.delete()
db.session.commit()

num_rows_deleted = Country.query.delete()
db.session.commit()


# Load country master data
# source: https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.json
obj_countries = []
with open('data/countries.json') as f:
    countries = json.load(f)
for c in countries:
    obj_countries.append(
        Country(
            name=c['name'],
            alpha2=c['alpha-2'],
            alpha3=c['alpha-3'],
            country_code=c['country-code'],
            region=c['region'],
            sub_region=c['sub-region'],
            intermediate_region=c['intermediate-region'],
            region_code=c['region-code'],
            sub_region_code=c['sub-region-code'],
            intermediate_region_code=c['intermediate-region-code'],
        )
    )
db.session.add_all(obj_countries)
db.session.commit()


# Load country master data
# source: https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.json
obj_states = []
with open('data/countries_states.json') as f:
    states = json.load(f)
for c in states['countries']:
    country_name = c['country']
    for s in c['states']:
        obj_states.append(
            State(
                name=s,
                country_name=country_name
            )
        )


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
           UOM(uom="g",
               longEN="gram",
               shortDE="g",
               type="2"),
           UOM(uom="mg",
               longEN="milligram",
               shortDE="mg",
               type="3"),
           UOM(uom="µg",
               longEN="micrograms",
               shortDE="µg",
               type="3"),
           UOM(uom="IU",
               longEN="international unit",
               shortDE="IE",
               type="3"),
           UOM(uom="kg",
               longEN="kilogram",
               shortDE="kg",
               type="1"),
           UOM(uom="l",
               longEN="liter",
               shortDE="l",
               type="1"),
           UOM(uom="ml",
               longEN="milliliter",
               shortDE="ml",
               type="1"),
           UOM(uom="tbsp",
               longEN="tablespoon",
               shortDE="El",
               type="1"),
           UOM(uom="tsp",
               longEN="teaspoon",
               shortDE="Tl",
               type="1"),
           UOM(uom="pn",
               longEN="pinch",
               shortDE="Prise",
               type="1"),
           UOM(uom="cup",
               longEN="cup",
               shortDE="Tasse",
               type="1"),
           UOM(uom="oz",
               longEN="shot",
               shortDE="Unze",
               type="1"),
           UOM(uom="pc",
               longEN="piece",
               shortDE="St",
               type="1"),
           UOM(uom="kcal",
               longEN="kilocalories",
               shortDE="kcal",
               type="3"),
           UOM(uom="x",
               longEN="unknown",
               shortDE="x",
               type="3")
]


# TODO: change field to say ndb nutrient mapping or so because other database have other terms for lookup
obj_nutrients = [
           Nutrient(value_uom="g",titleEN="Water",title="Wasser"),
           Nutrient(value_uom="kcal",titleEN="Energy",title="Energie"),
           Nutrient(value_uom="g",titleEN="Protein",title="Eiweis"),
           Nutrient(value_uom="g",titleEN="Total lipid (fat)",title="Fett"),
           Nutrient(value_uom="g",titleEN="Carbohydrate, by difference",title="Kohlenhydrate"),
           Nutrient(value_uom="g",titleEN="Fiber, total dietary",title="Ballaststoff"),
           Nutrient(value_uom="g",titleEN="Sugars, total",title="Zucker"),
           Nutrient(value_uom="mg",titleEN="Calcium, Ca",title="Kalzium"),
           Nutrient(value_uom="mg",titleEN="Iron, Fe",title="Eisen"),
           Nutrient(value_uom="mg",titleEN="Magnesium, Mg",title="Magnesium"),
           Nutrient(value_uom="mg",titleEN="Phosphorus, P",title="Phosphor"),
           Nutrient(value_uom="mg",titleEN="Potassium, K",title="Potassium"),
           Nutrient(value_uom="mg",titleEN="Sodium, Na",title="Sodium"),
           Nutrient(value_uom="mg",titleEN="Zinc, Zn",title="Zink"),
           Nutrient(value_uom="mg",titleEN="Vitamin C, total ascorbic acid",title="Vitamin C"),
           Nutrient(value_uom="mg",titleEN="Thiamin",title="Thiamin"),
           Nutrient(value_uom="mg",titleEN="Riboflavin",title="Riboflavin"),
           Nutrient(value_uom="mg",titleEN="Vitamin B-6",title="Vitamin B-6"),
           Nutrient(value_uom="µg",titleEN="Folate, DFE",title="Folsäure"),
           Nutrient(value_uom="µg",titleEN="Vitamin B-12",title="Vitamin B-12"),
           Nutrient(value_uom="µg",titleEN="Vitamin A, RAE",title="Vitamin A, RAE"),
           Nutrient(value_uom="IU",titleEN="Vitamin A, IU",title="Vitamin A, IU"),
           Nutrient(value_uom="mg",titleEN="Vitamin E (alpha-tocopherol)",title="Vitamin E"),
           Nutrient(value_uom="µg",titleEN="Vitamin D (D2 + D3)",title="Vitamin D (D2 + D3)"),
           Nutrient(value_uom="IU",titleEN="Vitamin D",title="Vitamin D"),
           Nutrient(value_uom="µg",titleEN="Vitamin K (phylloquinone)",title="Vitamin K"),
           Nutrient(value_uom="g",titleEN="Fatty acids, total saturated",title="gesättigte Fettsäuren"),
           Nutrient(value_uom="g",titleEN="Fatty acids, total monounsaturated",title="einfach ungesättigte Fettsäure"),
           Nutrient(value_uom="g",titleEN="Fatty acids, total polyunsaturated",title="mehrfach ungesättigte Fettsäure"),
           Nutrient(value_uom="g",titleEN="Fatty acids, total trans",title="trans-Fettsäuren"),
           Nutrient(value_uom="mg",titleEN="Cholesterol",title="Cholesterin"),
           Nutrient(value_uom="mg",titleEN="Caffeine",title="Koffein")
]

obj_materials = [
           Material(title="Zwiebel", language_code="de", standard_uom_id="pc"),
           Material(title="Curry", language_code="de", standard_uom_id="g"),
           Material(title="rote Linsen", language_code="de", standard_uom_id="g"),
           Material(title="Gemüsebrühe", language_code="de", standard_uom_id="g"),
           Material(title="Tomatenmark", language_code="de", standard_uom_id="g"),
           Material(title="gehackte Tomaten", language_code="de", standard_uom_id="g"),
           Material(title="Blumenkohl", language_code="de", standard_uom_id="pc"),
           Material(title="grüne Bohnen", language_code="de", standard_uom_id="g"),
           Material(title="frischer Koriander", language_code="de", standard_uom_id="g"),
           Material(title="griechischer Joghurt", language_code="de", standard_uom_id="g"),
           Material(title="Knoblauchzehe", language_code="de", standard_uom_id="pc"),
           Material(title="Olivenöl", language_code="de", standard_uom_id="l"),
           Material(title="Salz", language_code="de", standard_uom_id="g"),
           Material(title="schwarzer Pfeffer", language_code="de", standard_uom_id="g"),
           Material(title="Zucker", language_code="de", standard_uom_id="g"),
           Material(title="Wasser", language_code="de", standard_uom_id="l"),
           Material(title="Stange Lauch", language_code="de", standard_uom_id="pc"),
           Material(title="Karotte", language_code="de", standard_uom_id="pc"),
           Material(title="Knollensellerie, mittelgroß", language_code="de", standard_uom_id="g"),
           Material(title="Linsen", language_code="de", standard_uom_id="g"),
           Material(title="Räucherbauch", language_code="de", standard_uom_id="g"),
           Material(title="Kartoffel", language_code="de", standard_uom_id="pc"),
           Material(title="Wienerle", language_code="de", standard_uom_id="pc"),
           Material(title="Öl", language_code="de", standard_uom_id="l"),
           Material(title="Muskat", language_code="de", standard_uom_id="g"),
           Material(title="Rotweinessig", language_code="de", standard_uom_id="l"),
           Material(title="Spätzle", language_code="de", standard_uom_id="g"),
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
                      material=obj_materials[0]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[4],
                      meal=obj_meals[0],
                      title="Curry",
                      material=obj_materials[1]
                      ),
           Ingredient(quantity=100,
                      uom=obj_uoms[0],
                      meal=obj_meals[0],
                      title="rote Linsen",
                      material=obj_materials[2]
                      ),
           Ingredient(quantity=200,
                      uom=obj_uoms[3],
                      meal=obj_meals[0],
                      title="Gemüsebrühe",
                      material=obj_materials[3]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[4],
                      meal=obj_meals[0],
                      title="Tomatenmark",
                      material=obj_materials[4]
                      ),
           Ingredient(quantity=400,
                      uom=obj_uoms[0],
                      meal=obj_meals[0],
                      title="gehackte Tomaten",
                      material=obj_materials[5]
                      ),
           Ingredient(quantity=2,
                      uom=obj_uoms[7],
                      meal=obj_meals[0],
                      title="Blumenkohl",
                      material=obj_materials[6]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[7],
                      meal=obj_meals[0],
                      title="grüne Bohnen",
                      material=obj_materials[7]
                      ),
           Ingredient(quantity=2,
                      uom=obj_uoms[4],
                      meal=obj_meals[0],
                      title="frischer Koriander",
                      material=obj_materials[8]
                      ),
           Ingredient(quantity=5,
                      uom=obj_uoms[4],
                      meal=obj_meals[0],
                      title="griechischer Joghurt",
                      material=obj_materials[9]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[9],
                      meal=obj_meals[0],
                      title="Knoblauchzehe",
                      material=obj_materials[10]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[4],
                      meal=obj_meals[0],
                      title="Olivenöl",
                      material=obj_materials[11]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[6],
                      meal=obj_meals[0],
                      title="Salz",
                      material=obj_materials[12]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[6],
                      meal=obj_meals[0],
                      title="schwarzer Pfeffer",
                      material=obj_materials[13]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[5],
                      meal=obj_meals[0],
                      title="Zucker",
                      material=obj_materials[14]
                      ),
           Ingredient(quantity=200,
                      uom=obj_uoms[3],
                      meal=obj_meals[0],
                      title="Wasser",
                      material=obj_materials[15]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[9],
                      meal=obj_meals[1],
                      title="Zwiebel",
                      material=obj_materials[0]
                      ),
           Ingredient(quantity=0.5,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      title="Stange Lauch",
                      material=obj_materials[16]
                      ),
           Ingredient(quantity=50,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      title="Karotte",
                      material=obj_materials[17]
                      ),
           Ingredient(quantity=50,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      title="Knollensellerie, mittelgroß",
                      material=obj_materials[18]
                      ),
           Ingredient(quantity=50,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      title="Linsen",
                      material=obj_materials[19]
                      ),
           Ingredient(quantity=50,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      title="Räucherbauch",
                      material=obj_materials[20]
                      ),
           Ingredient(quantity=50,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      title="Gemüsebrühe",
                      material=obj_materials[3]
                      ),
           Ingredient(quantity=1,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      title="Kartoffel",
                      material=obj_materials[21]
                      ),
           Ingredient(quantity=4,
                      uom=obj_uoms[9],
                      meal=obj_meals[1],
                      title="Wienerle",
                      material=obj_materials[22]
                      ),
           Ingredient(quantity=2,
                      uom=obj_uoms[4],
                      meal=obj_meals[1],
                      title="Öl",
                      material=obj_materials[23]
                      ),
           Ingredient(quantity=2,
                      uom=obj_uoms[4],
                      meal=obj_meals[1],
                      title="Salz",
                      material=obj_materials[12]
                      ),
           Ingredient(quantity=2,
                      uom=obj_uoms[4],
                      meal=obj_meals[1],
                      title="schwarzer Pfeffer",
                      material=obj_materials[13]
                      ),
           Ingredient(quantity=2,
                      uom=obj_uoms[4],
                      meal=obj_meals[1],
                      title="Rotweinessig",
                      material=obj_materials[24]
                      ),
           Ingredient(quantity=250,
                      uom=obj_uoms[0],
                      meal=obj_meals[1],
                      title="Spätzle",
                      material=obj_materials[25]
                      ),
]


obj_places = [
    Place(
        titleEN='NORMA Frauenaurach',
        title='NORMA Frauenaurach',
        google_place_id='ChIJe5c7N0H_oUcRg62tY-FBrVA',
        geo_lat='49.561972',
        geo_lng='10.961898',
        ),
    Place(
        titleEN='Dorfladen Hüttendorf',
        title='Dorfladen Hüttendorf',
        google_place_id='ChIJn3nyUHL_oUcRR_VbmRcwF-w',
        geo_lat='49.548049',
        geo_lng='10.961172',
        ),
    Place(
        titleEN='Edeka Neumühle',
        title='Edeka Neumühle',
        google_place_id='ChIJ4-bDBrf4oUcRYofAX6KmRUU',
        geo_lat='49.588103',
        geo_lng='10.977139',
        )
            ]


db.session.add_all(obj_states)
db.session.add_all(obj_users)
db.session.add_all(obj_uoms)
db.session.add_all(obj_nutrients)
db.session.add_all(obj_materials)
db.session.add_all(obj_meals)
db.session.add_all(obj_ingredients)
db.session.add_all(obj_places)
db.session.commit()
