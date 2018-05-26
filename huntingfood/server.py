from huntingfood import app
from huntingfood.users.authentication import login_required

import os  # required to have access to the Port environment variable
import json

import pprint  # for debugging purposes

# Enable logging of events
import logging

# Google cloud authentication & configuration
from google.oauth2 import service_account

from google.cloud import translate  # for google translator api
from google.cloud import language  # for google natural language api

# added due to google oauth login feature
from flask import make_response
from flask import session as login_session  # a dictionary to store information

# National Nutrient Database - United States Department of Agriculture
from huntingfood import ndb

from datetime import datetime

# Required to convert time zone aware date strings from Json into a date object
import dateutil.parser

from flask import render_template, request, url_for, redirect, \
    jsonify, send_from_directory
from werkzeug.utils import secure_filename  # required for file upload
from sqlalchemy import exc, and_, or_

# Import own modules
from huntingfood import tools
from huntingfood import db
from huntingfood.models import UOM, Meal, Ingredient, Material, MaterialForecast
from huntingfood.models import FoodComposition, Nutrient
from huntingfood.models import FoodMainGroup
from huntingfood.models import InventoryItem, Inventory, DietPlan, DietPlanItem
from huntingfood.models import Place
# Marshmallow Schemas
from huntingfood.models import InventoryItemSchema, MaterialForecastSchema

# Set Logging level
logger = logging.getLogger()
logger.setLevel(logging.INFO)
pp = pprint.PrettyPrinter(indent=1)

# TODO: not really required but just to ease the migration to flask-sqlalchemy
session = db.session

db.create_all()
db.session.commit()

# Create Marshmallow schema dumpers
inventory_item_schema = InventoryItemSchema(many=True)
material_forecast_schema = MaterialForecastSchema(many=True)


# Google Cloud Connection
PK_escaped = app.config['GOOGLE_CLOUD_CREDENTIALS_PK']
PK_raw = PK_escaped.replace('\\n', '\n')
service_account_info = dict(
    type='service_account',
    project_id='long-memory-188919',
    private_key_id='b26b39e14a2375751b5064b77e426243b4625de4',
    private_key=PK_raw,
    client_email='serviceaccount-owner@long-memory-188919.iam.gserviceaccount.com',  # noqa
    client_id='106478515271128625146',
    auth_uri='https://accounts.google.com/o/oauth2/auth',
    token_uri='https://accounts.google.com/o/oauth2/token',
    auth_provider_x509_cert_url='https://www.googleapis.com/oauth2/v1/certs',
    client_x509_cert_url='https://www.googleapis.com/robot/v1/metadata/x509/serviceaccount-owner%40long-memory-188919.iam.gserviceaccount.com'  # noqa
)
SCOPES = ['https://www.googleapis.com/auth/cloud-language',
          'https://www.googleapis.com/auth/cloud-translation']
google_cloud_credentials = service_account \
    .Credentials \
    .from_service_account_info(
        service_account_info,
        scopes=SCOPES)

# Google translate client
translate_client = translate.Client(target_language='en',
                                    credentials=google_cloud_credentials)
language_client = language.LanguageServiceClient(
    credentials=google_cloud_credentials)

# TODO: Validate if there is a better way in sqlAlchemy ot achieve that
# TODO: Ensure reload of dictionary when uom table changes
nutrientDict = {}
items = Nutrient.query
for i in items:
    nutrientDict.update({i.titleEN: i.id})

uomDict = {}
items = UOM.query
for i in items:
    uomDict.update({i.uom: i.type})


@app.route('/testpage')
def testpage():
    return render_template("testpage.html")


@app.route('/map')
def map():
    return render_template(
        "map.html",
        loginSession=login_session,
        g_api_key=app.config['GOOGLE_API_KEY'])


# Custom Static folders
@app.route('/css/<path:filename>')
def css_static(filename):
    return send_from_directory('static/css', filename)


@app.route('/js/<path:filename>')
def js_static(filename):
    return send_from_directory('static/js', filename)


@app.route('/font/<path:filename>')
def font_static(filename):
    return send_from_directory('static/font', filename)


@app.route('/img/<path:filename>')
def img_static(filename):
    return send_from_directory('static/img', filename)


@app.route('/sass/<path:filename>')
def sass_static(filename):
    return send_from_directory('static/sass', filename)


@app.route('/upload/<path:filename>')
def upload_static(filename):
    return send_from_directory('upload', filename)


@app.route('/')
def showHome():
    return render_template("index.html")


@app.route('/meals')
def showMeals():
    meals = Meal.query.all()
    return render_template(
        "meals.html",
        meals=meals,
        getIngredients=getIngredients,
        loginSession=login_session)


@app.route('/food_facts')
def showFoodFacts():
    return render_template("food_facts.html")


@app.route('/shoppinglist')
@login_required
def showShoppingList():
    # TODO: If member of a group filter by group and not by creator
    meals = Meal.query.filter_by(
        owner_id=login_session['user_id']).all()
    diet_plan = DietPlan.query.filter_by(
        id=login_session['default_diet_plan_id']).first()
    inventory = Inventory.query.filter_by(
        id=login_session['default_inventory_id']).first()

    return render_template(
        "shoppinglist.html",
        meals=meals,
        diet_plan=diet_plan,
        inventory=inventory,
        getIngredients=getIngredients,
        loginSession=login_session,  # TODO: is that necessary to pass it to the client?
        g_api_key=app.config['GOOGLE_API_KEY'])


@app.route('/shoppinglist/items', methods=['GET', 'POST'])
def all_shopping_items_handler():

    inventory_items = []

    if request.method == 'POST':
        title = request.form.get('title')
        inventory_item = InventoryItem(titleDE=title, level=0)
        session.add(inventory_item)
        session.commit()
        inventory_items.append(inventory_item)
        return jsonify(inventory_items=[i.serialize for i in inventory_items])

    elif request.method == 'GET':
        inventory_items = InventoryItem.query.all()
        # TODO: return nested structures including inventory header and user
        # information with https://flask-marshmallow.readthedocs.io/en/latest/
        return jsonify(inventory_items=[i.serialize for i in inventory_items])


# TODO: Think of combining both endpoints into one
@app.route('/shoppinglist/item', methods=['GET', 'DELETE', 'PUT'])
def shopping_item_handler():

    inventory_items = []

    id = request.form.get('id')
    inventory_item = InventoryItem.query.filter_by(id=id).one()

    if request.method == 'GET':
        inventory_items.append(inventory_item)
        return jsonify(inventory_items=[i.serialize for i in inventory_items])

    elif request.method == 'DELETE':
        session.delete(inventory_item)
        session.commit()
        return "item deleted"

    elif request.method == 'PUT':
        titleDE = request.args.get('title')
        level = request.args.get('level')
        if titleDE:
            inventory_item.titleDE = titleDE
        if level:
            inventory_item.level = level
        session.commit()
        inventory_items.append(inventory_item)
        return jsonify(inventory_items=[i.serialize for i in inventory_items])


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# API Endpoints
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@app.route('/api/v1/meals', methods=['GET'])
def api_v1_meals():
    if request.method == 'GET':
        meals = Meal.query.filter_by(owner_id=login_session['user_id']).all()
        return jsonify(meals=[m.serialize for m in meals])


@app.route('/api/v1/dietplan/<int:diet_plan_id>', methods=['GET', 'POST', 'DELETE', 'PUT'])
def api_v1_dietplan(diet_plan_id):
    dp_items = []
    if request.method == 'GET':
        plan_date = request.args.get('plan_date')
        if plan_date:
            dp_items = DietPlanItem.query.filter_by(
                diet_plan_id=diet_plan_id,
                plan_date=plan_date).all()
        else:
            dp_items = DietPlanItem.query.filter_by(
                diet_plan_id=diet_plan_id).all()
        return jsonify(diet_plan_items=[i.serialize for i in dp_items])

    if request.method == 'POST':
        plan_date = dateutil.parser.parse(request.form.get('plan_date')).date()
        meal_id = request.form.get('meal_id')
        consumed = request.form.get('consumed')
        portions = request.form.get('portions')

        if (plan_date) and (meal_id):

            # Step 1: Create DIET PLAN ITEM
            diet_plan_item = DietPlanItem(
                diet_plan_id=diet_plan_id,
                plan_date=plan_date,
                meal_id=meal_id,
                consumed=tools.str_to_bool(consumed),
                portions=tools.str_to_numeric(portions)
                )
            session.add(diet_plan_item)
            session.commit()

            # Step 2: Identify INVENTORY_ITEMS that are missing
            # for each food item refernced in the meal ingredients
            # if the item does not yet exist in the inventory
            try:
                missing_inventory_items = Material.query.\
                    select_from(Material).\
                    outerjoin(Material.referencedIn).\
                    outerjoin(Material.referencedInventoryItem).\
                    filter(Ingredient.meal_id == meal_id).\
                    filter(InventoryItem.material_id == None).all()
            except NoRecordsError:
                logging.info('No records found')
            except exc.SQLAlchemyError:
                logging.exception('Some problem occurred')

            logging.info('Missing Inventory items = ' + str(len(missing_inventory_items)) + ' for Meal Id = ' + meal_id)

            # Step 3: Create INVENTORY_ITEM that are missing
            for row in missing_inventory_items:
                logging.info("Generate inventory items: " + str(row.titleEN))
                if (row.titleEN):
                    inventory_item = InventoryItem(
                        inventory_id=login_session['default_inventory_id'],  # TODO: what if the user wants to update another inventory?
                        titleEN=row.titleEN,
                        titleDE=row.titleDE,
                        status=1,
                        material_id=row.id,
                        level=0,
                        sku_uom=row.standard_uom_id,
                        re_order_level=99,
                        re_order_quantity=99
                        )
                    session.add(inventory_item)
                    session.commit()

            # Step 4: Determine all materials related to the meal
            try:
                logging.info('Determine all materials ...')
                materials = db.session.query(Material, Ingredient, Meal).\
                    join(Material.referencedIn).\
                    join(Ingredient.meal).\
                    filter(Ingredient.meal_id == meal_id).all()
            except NoRecordsError:
                logging.info('No materials found')
            except exc.SQLAlchemyError:
                logging.exception('Some problem occurred')

            # Step 5: Determine all materials with forecast and update them
            try:
                logging.info('Determine existing material forecasts ...')
                planned_materials = db.session.query(Material, Ingredient, Meal, MaterialForecast).\
                    join(Material.referencedIn).\
                    join(Material.referencedMaterialForecast).\
                    join(Ingredient.meal).\
                    filter(Ingredient.meal_id == meal_id).\
                    filter(MaterialForecast.plan_date == plan_date).\
                    filter(MaterialForecast.inventory_id == login_session['default_inventory_id']).all()
            except NoRecordsError:
                logging.info('No existing material forecasts')
            except exc.SQLAlchemyError:
                logging.exception('Some problem occurred')

            for row in planned_materials:
                logging.info("Old MaterialForecast ("
                             + str(row.Material.id) + ") = "
                             + str(row.MaterialForecast.quantity))
                row.MaterialForecast.quantity = row.MaterialForecast.quantity + (float(portions)/row.Meal.portions) * row.Ingredient.quantity
                logging.info("New MaterialForecast ("
                             + str(row.Material.id) + ") = "
                             + str(row.MaterialForecast.quantity))

                # for materials with forecast remove the records from
                # the all material list
                for m in materials:
                    if (m.Material.id == row.Material.id):
                        materials.remove(m)

            session.commit()

            # Step 6: Create new forecast for all remaining materials in the
            # materials list
            for row in materials:
                new_material_forecast = MaterialForecast(
                    inventory_id=login_session['default_inventory_id'],
                    material_id=row.Material.id,
                    plan_date=plan_date,
                    quantity=row.Ingredient.quantity,
                    quantity_uom=row.Ingredient.uom_id
                )
                session.add(new_material_forecast)
            session.commit()

            # Step 6: Return Response
            dp_item = DietPlanItem.query.filter_by(
                id=diet_plan_item.id).all()
            return jsonify(diet_plan_item=[i.serialize for i in dp_item])
        else:
            response = make_response(json.dumps(
                'Missing key fields to create a diet plan item (meal_id, plan_date, diet_plan_id).'), 400)
            response.headers['Content-Type'] = 'application/json'
            return response

    if request.method == 'PUT':
        plan_date = dateutil.parser.parse(request.form.get('plan_date')).date()
        meal_id = request.form.get('meal_id')
        id = request.form.get('id')
        consumed = request.form.get('consumed')
        portions = request.form.get('portions')

        diet_plan_item = DietPlanItem.query.filter_by(id=id).one_or_none()
        dp_plan_date = diet_plan_item.plan_date

        if (plan_date != dp_plan_date):
            response = make_response(json.dumps(
                'Can not change item because it is not allowed to change the plan_date'), 400)
            response.headers['Content-Type'] = 'application/json'
            return response

        if (id) and (diet_plan_item):
            diet_plan_item.meal_id = meal_id
            diet_plan_item.consumed = tools.str_to_bool(consumed)
            diet_plan_item.portions = tools.str_to_numeric(portions)
            session.commit()

            updateMaterialForecast(diet_plan_id, login_session['default_inventory_id'], plan_date)

            response = make_response(json.dumps(
                'Item successfully updated'), 200)
            response.headers['Content-Type'] = 'application/json'
            return response
        else:
            response = make_response(json.dumps(
                'Can not change item because item was not found'), 400)
            response.headers['Content-Type'] = 'application/json'
            return response

    if request.method == 'DELETE':
        id = request.form.get('id')
        diet_plan_item = DietPlanItem.query.filter_by(id=id).one_or_none()
        plan_date = diet_plan_item.plan_date

        if (id) and (diet_plan_item):
            session.delete(diet_plan_item)
            session.commit()

            updateMaterialForecast(diet_plan_id, login_session['default_inventory_id'], plan_date)

            response = make_response(json.dumps(
                'Item successfully deleted'), 200)
            response.headers['Content-Type'] = 'application/json'
            return response
        else:
            response = make_response(json.dumps(
                'Can not delete item because item was not found'), 400)
            response.headers['Content-Type'] = 'application/json'
            return response


@app.route('/api/v1/inventory/<int:inventory_id>', methods=['GET', 'POST', 'DELETE', 'PUT'])
def api_v1_inventory(inventory_id):
    inventory_items = []

    if request.method == 'GET':
        inventory_items = db.session.query(InventoryItem).all()
        result = inventory_item_schema.dump(inventory_items).data
        return jsonify({'inventory_items': result})

    if request.method == 'POST':
        titleEN = request.form.get('titleEN')
        titleDE = request.form.get('titleDE')
        status = request.form.get('status')
        material_id = request.form.get('material_id')
        level = request.form.get('level')
        need_from_diet_plan = request.form.get('need_from_diet_plan')
        need_additional = request.form.get('need_additional')
        re_order_level = request.form.get('re_order_level')
        re_order_quantity = request.form.get('re_order_quantity')

        if (titleDE) and (status):
            inventory_item = InventoryItem(
                inventory_id=inventory_id,
                titleEN=titleEN,
                titleDE=titleDE,
                status=tools.str_to_numeric(status),
                material_id=tools.str_to_numeric(material_id),
                level=tools.str_to_numeric(level),
                need_from_diet_plan=tools.str_to_numeric(need_from_diet_plan),
                need_additional=tools.str_to_numeric(need_additional),
                re_order_level=tools.str_to_numeric(re_order_level),
                re_order_quantity=tools.str_to_numeric(re_order_quantity)
                )
            session.add(inventory_item)
            session.commit()
            # TODO: avoid calling again the database when all data is in the
            # session, solve problem that object is not iterable
            inventory_item = InventoryItem.query.filter_by(
                id=inventory_item.id).all()
            return jsonify(inventory_item=[i.serialize for i in inventory_item])
        else:
            response = make_response(json.dumps(
                'Missing key fields to create an inventory item (titleDE, status).'), 400)
            response.headers['Content-Type'] = 'application/json'
            return response

    if request.method == 'PUT':
        id = request.form.get('id')
        titleEN = request.form.get('titleEN')
        titleDE = request.form.get('titleDE')
        status = request.form.get('status')
        material_id = request.form.get('material_id')
        level = request.form.get('level')
        need_from_diet_plan = request.form.get('need_from_diet_plan')
        need_additional = request.form.get('need_additional')
        re_order_level = request.form.get('re_order_level')
        re_order_quantity = request.form.get('re_order_quantity')
        ignore_forecast = request.form.get('ignore_forecast')

        inventory_item = InventoryItem.query.filter_by(id=id).one_or_none()

        if (id) and (inventory_item):
            inventory_item.titleEN = titleEN,
            inventory_item.titleDE = titleDE,
            inventory_item.status = tools.str_to_numeric(status),
            inventory_item.material_id = tools.str_to_numeric(material_id),
            inventory_item.level = tools.str_to_numeric(level),
            inventory_item.need_from_diet_plan = tools.str_to_numeric(need_from_diet_plan),
            inventory_item.need_additional = tools.str_to_numeric(need_additional),
            inventory_item.re_order_level = tools.str_to_numeric(re_order_level),
            inventory_item.re_order_quantity = tools.str_to_numeric(re_order_quantity)
            inventory_item.ignore_forecast = tools.str_to_bool(ignore_forecast)

            session.commit()
            response = make_response(json.dumps(
                'Item successfully updated'), 200)
            response.headers['Content-Type'] = 'application/json'
            return response
        else:
            response = make_response(json.dumps(
                'Can not change item because item was not found'), 400)
            response.headers['Content-Type'] = 'application/json'
            return response

    if request.method == 'DELETE':
        id = request.form.get('id')
        inventory_item = InventoryItem.query.filter_by(id=id).one_or_none()

        if (id) and (inventory_item):
            session.delete(inventory_item)
            session.commit()
            response = make_response(json.dumps(
                'Item successfully deleted'), 200)
            response.headers['Content-Type'] = 'application/json'
            return response
        else:
            response = make_response(json.dumps(
                'Can not delete item because item was not found'), 400)
            response.headers['Content-Type'] = 'application/json'
            return response


@app.route('/shoppinglist/map/places', methods=['GET', 'POST'])
def map_places_handler():

    places = []

    if request.method == 'POST':
        return 'not yet implemented'

    elif request.method == 'GET':
        places = Place.query.all()
        return jsonify(places = [i.serialize for i in places])


@app.route('/meals/add', methods=['GET','POST'])
@login_required
def addMeals():
    if request.method == 'POST' and request.form['button'] == "Save":
        print("Start file handler")
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
            print("filepath = " + filepath)
            file.save(filepath)

        # ---- MEAL CREATION -----
        newMeal = Meal(title=request.form['title'],
                       description=request.form['description'],
                       portions=request.form['portions'],
                       calories="410 - 780",
                       image=filename,
                       owner_id=login_session['user_id'])
        session.add(newMeal)
        session.commit()

        #---- INGREDIENTS CREATION ----



        # TODO: Optimize the creation of food and ingredient objects
        #      by avoiding too many commits

        x = 1
        while request.form['ingredient'+str(x)]:
            row = str(x)
            ingredient_text = request.form['ingredient'+row]
            ingredient_uom = request.form['uom'+row]
            user_language = login_session['language']

            if (user_language != 'en'):
                # Translate user language to en
                translation = translate_client.translate(
                    ingredient_text, source_language=login_session['language'])
                ingredient_text_EN = translation['translatedText']
                print("newIngredient.titleEN = " + ingredient_text_EN)
            else:
                ingredient_text_EN = ingredient_text

            # Identify food entity from entered text using language processing
            # use en language to improve results since en splits combined
            # german words
            food_entity = analyze_ingredient(
                translation['translatedText'], language='en')
            print("Food entity: %s" % food_entity)

            # Query a food database (e.g. NDB) to retrieve nutrient information
            # and to create a food master data record. The id of such a record
            # is returned if a match in the food database was found.
            material_id = getFood(ingredient_text_EN, ingredient_text, ingredient_uom)
            if not material_id:
                material_id = None

            # Add new ingredient into database
            newIngredient = Ingredient(quantity=request.form['quantity'+row],
                                       uom_id=ingredient_uom,
                                       meal_id=newMeal.id,
                                       title=ingredient_text,
                                       titleEN=translation['translatedText'],
                                       base_food_part=food_entity,
                                       material_id=material_id)

            session.add(newIngredient)
            session.commit()

            x += 1

        return redirect(url_for("showMeals"))

    elif request.method == 'POST' and request.form['button'] == "Cancel":
        print("POST button = Cancel")
        meals = Meal.query
        return render_template("meals.html",meals=meals,getIngredients=getIngredients)
    else:  # 'GET':
        print("GET")
        uoms = UOM.query
        materials = Material.query
        return render_template("meals_add.html",uoms=uoms,materials=materials)


@app.route('/meals/delete/<int:meal_id>', methods=['GET', 'POST'])
@login_required
def deleteMeal(meal_id):

    o = Meal.query.filter_by(id=meal_id).one()
    if request.method == 'POST' and request.form['button'] == "Delete":
        session.delete(o)
        session.commit()
        # TODO: flash("Meal deleted")
        # TODO: Delete image file from folder
        return redirect(url_for('showMeals'))
    elif request.method == 'GET':
        return render_template("meals_delete.html",meal=o)
    else:
        return redirect(url_for("showMeals"))


@app.route('/meals/view/<int:meal_id>')
def showMeal(meal_id):
    o = Meal.query.filter_by(id=meal_id).one()
    return render_template("meal_view.html",meal=o,getIngredients=getIngredients)


# Food database helper functions
# TODO: Rework material creation
def getFood(keyword, keyword_local_language, standard_uom):
    # Account Email: mailboxsoeren@gmail.com
    # Account ID: 738eae59-c15d-4b89-a621-bcd7182a51e2

    if app.config['NDB_KEY']:
        n = ndb.NDB(app.config['NDB_KEY'])
        results = n.search_keyword(keyword)
        if results:

            i = list(results['items'])[0]  # TODO: identify relevant item, for now take the first one
            print("Found NDB item: "+i.get_name())

            # Create Food Main Group
            foodMainGroup = FoodMainGroup.query.filter_by(titleEN=i.get_group()).first()
            if not foodMainGroup:
                logging.info('Create FoodMainGroup: ' + i.get_group())
                foodMainGroup = FoodMainGroup(titleEN=i.get_group())
                session.add(foodMainGroup)
                session.commit()

            # Create Food
            food = Material.query.filter_by(titleEN=i.get_name()).first()
            if not food:
                logging.info('Create Material: ' + i.get_name())
                food = Material(
                    titleEN=i.get_name(),
                    titleDE=keyword_local_language,
                    standard_uom_id=standard_uom,
                    ndb_code=i.get_ndbno(),
                    food_maingroup_id=foodMainGroup.id)
                session.add(food)
                session.commit()

                # Create Nutrients
                report = n.food_report(i.get_ndbno())

                nutrients = report['food'].get_nutrients()
                for n in nutrients:
                    # use existing nutrient object if exists
                    if n.get_name() in nutrientDict:
                        nutriendID = nutrientDict[n.get_name()]  # retreive internal id based on the titleEN

                    # create new nutrient object
                    else:
                        logging.info('Create Nutrient: ' + n.get_name())
                        translated_text = translate_client.translate(
                            n.get_name(), target_language='de')['translatedText']
                        newNutrient = Nutrient(value_uom=n.get_unit(),
                                               titleEN=n.get_name(),
                                               titleDE=translated_text)
                        session.add(newNutrient)
                        session.commit()

                        nutriendID = newNutrient.id
                        # TODO: Improve caching of nutrients via dictionnary overall
                        nutrientDict[n.get_name()] = nutriendID

                    # TODO: all get into unknown atm
                    if n.get_unit() in uomDict:
                        uomID = n.get_unit()
                    else:
                        logging.info('unknown unit of measure of nutrient')
                        uomID = "x"  # TODO: improve later

                    logging.info('Create FoodComposition')
                    fc = FoodComposition(material_id=food.id,
                                        nutrient_id=nutriendID,
                                        per_qty_uom=uomID,
                                        per_qty=100,
                                        value=n.get_value())
                    session.add(fc)
                    session.commit()
            return food.id
        else:
            print("No results in NDB found")
            return None
    else:
        print("Missing API Key in Environment Variable")
        return None


def analyze_ingredient(ingredient_text, **kwargs):

    target_language = kwargs['language']

    # Create a whole sentence so the language api understands the context
    # and provides better results
    intro_text = {
        'de': 'Die Speise besteht aus',
        'en': 'The meal consists of'
    }

    # Using google language api to identify
    # adjectives = processing (pre or at home)
    # nouns = custom UOM and ingredients/food
    # conjunctions = "and", "or", etc. for alternatives
    # Reference:
    # https://cloud.google.com/natural-language/docs/reference/rest/v1/Token
    content = ' '.join([intro_text[target_language], ingredient_text])
    print("content: %s" % content)
    document = language.types.Document(
        content=content,
        type=language.enums.Document.Type.PLAIN_TEXT,
        language=target_language)
    response = language_client.analyze_syntax(
        document=document,
        encoding_type='UTF32')
    tokens = response.tokens

    # part-of-speech tags from enums.PartOfSpeech.Tag
    # reference: https://cloud.google.com/natural-language/docs/reference/rest/v1/Token#partofspeech
    pos_tag = ('UNKNOWN', 'ADJ', 'ADP', 'ADV', 'CONJ', 'DET', 'NOUN', 'NUM',
           'PRON', 'PRT', 'PUNCT', 'VERB', 'X', 'AFFIX')

    parse_label = ('UNKNOWN', 'ABBREV', 'ACOMP', 'ADVCL', 'ADVMOD', 'AMOD',
           'APPOS', 'ATTR', 'AUX', 'AUXPASS', 'CC', 'CCOMP', 'CONJ', 'CSUBJ',
           'CSUBJPASS', 'DEP', 'DET', 'DISCOURSE', 'DOBJ', 'EXPL', 'GOESWITH',
           'IOBJ', 'MARK', 'MWE', 'MWV', 'NEG', 'NN', 'NPADVMOD', 'NSUBJ',
           'NSUBJPASS', 'NUM', 'NUMBER', 'P', 'PARATAXIS', 'PARTMOD', 'PCOMP',
           'POBJ', 'POSS', 'POSTNEG', 'PRECOMP', 'PRECONJ', 'PREDET', 'PREF',
           'PREP', 'PRONL', 'PRT', 'PS', 'QUANTMOD', 'RCMOD', 'RCMODREL',
           'RDROP', 'REF', 'REMNANT', 'REPARANDUM', 'ROOT', 'SNUM', 'SUFF',
           'TMOD', 'TOPIC', 'VMOD', 'VOCATIVE', 'XCOMP', 'SUFFIX', 'TITLE',
           'ADVPHMOD', 'AUXCAUS', 'AUXVV', 'DTMOD', 'FOREIGN', 'KW', 'LIST',
           'NOMC', 'NOMCSUBJ', 'NOMCSUBJPASS', 'NUMC', 'COP', 'DISLOCATED',
           'ASP', 'GMOD', 'GOBJ', 'INFMOD', 'MES', 'NCOMP')

    #counter = 0
    skip_intro_words = 4
    return_value = None

    # TODO: Implement natural language semantic relationship identification between entities in order to understand the base food entity
    # for example 'clove of garlic' should return garlic and not clove
    # wheat flour should return wheat flour
    # noun + "of" could be understood as a component of the whole as custom uom
    # current workaround case to identify the base food entity:
    # 1) Take all entities (nouns) that are noun compound notifiers (label = nn)
    # 2) Take the last entity that is a object of a preposition (label = pobj)
    # 3) Take all nouns

    # Alternative loop for testing
    index = 0
    for sentence in response.sentences:
        content  = sentence.text.content  # sentence['text']['content']
        sentence_begin = sentence.text.begin_offset  #['text']['beginOffset']
        sentence_end = sentence_begin + len(content) - 1
        case = 0  # ensures that once a matching case is found it locks it
        while index < len(response.tokens) and response.tokens[index].text.begin_offset <= sentence_end:
            token = tokens[index]
            token_parse_label = parse_label[token.dependency_edge.label]
            token_pos_tag = pos_tag[token.part_of_speech.tag]
            print(u'{} - {}: {} - {} - {}'.format(index,pos_tag[token.part_of_speech.tag],token.text.content,token.dependency_edge.head_token_index,parse_label[token.dependency_edge.label]))
            #TODO: Skip intro sentence part

            if ((index + 1) > skip_intro_words):
                if token_parse_label == 'NN':
                    case = 3
                    if return_value is None:
                        return_value = token.lemma
                    else:
                        return_value = return_value + ' ' + token.lemma
                elif (case < 3) and (token_parse_label == 'POBJ'):
                    case = 2
                    return_value = token.lemma
                elif (case < 2) and (token_pos_tag == 'NOUN'):
                    case = 1
                    if return_value is None:
                        return_value = token.lemma
                    else:
                        return_value = return_value + ' ' + token.lemma

            index += 1

    return return_value


def getIngredients(meal_id):
    if meal_id:
        items = Ingredient.query.filter_by(meal_id=meal_id)
        return items
    else:
        return false


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in \
           app.config['ALLOWED_EXTENSIONS']


# TODO: Improve:
# 1) Running this in the database using joints, group by and sum
# 2) Create def for creation of inventory so there is only one point where inventories are created
def updateMaterialForecast(diet_plan_id, inventory_id, plan_date):

    # Step 1: Delete all forecasts for the given plan date and inventory
    try:
        logging.info('DELETE all Forecasts ...')
        forecasts = db.session.query(MaterialForecast).\
            filter(MaterialForecast.inventory_id == inventory_id).\
            filter(MaterialForecast.plan_date == plan_date).\
            delete(synchronize_session=False)
    except NoRecordsError:
        logging.info('No existing material forecasts')
    except exc.SQLAlchemyError:
        logging.exception('Some problem occurred during deletion of MaterialForecasts')

    # session.delete(forecasts)
    session.commit()

    # Step 2: Determine all meals in a dietplan for a plan date
    try:
        diet_plan_items = DietPlanItem.query.\
            select_from(DietPlanItem).\
            filter(DietPlanItem.diet_plan_id == diet_plan_id).\
            filter(DietPlanItem.plan_date == plan_date).all()
    except NoRecordsError:
        logging.info('No records found')
    except exc.SQLAlchemyError:
        logging.exception('Some problem occurred')

    for dp_item in diet_plan_items:
        # Step 2: Identify missing inventory items and create them
        try:
            missing_inventory_items = Material.query.\
                select_from(Material).\
                outerjoin(Material.referencedIn).\
                outerjoin(Material.referencedInventoryItem).\
                filter(Ingredient.meal_id == dp_item.meal_id).\
                filter(InventoryItem.material_id == None).all()
        except NoRecordsError:
            logging.info('No records found')
        except exc.SQLAlchemyError:
            logging.exception('Some problem occurred')

        logging.info('Missing Inventory items = ' + str(len(missing_inventory_items)) + ' for Meal Id = ' + str(dp_item.meal_id))
        for inv_item in missing_inventory_items:
            logging.info("Create inventory items: " + str(inv_item.titleEN))
            if (inv_item.titleEN):
                inventory_item = InventoryItem(
                    inventory_id=login_session['default_inventory_id'],  # TODO: what if the user wants to update another inventory?
                    titleEN=inv_item.titleEN,
                    titleDE=inv_item.titleDE,
                    material_id=inv_item.id,
                    level=0,
                    sku_uom=inv_item.standard_uom_id,
                    re_order_level=99,
                    re_order_quantity=99
                    )
                session.add(inventory_item)
                session.commit()

        # Step 3: Determine all materials related to the meal
        try:
            logging.info('Determine all materials ...')
            materials = db.session.query(Material, Ingredient, Meal).\
                join(Material.referencedIn).\
                join(Ingredient.meal).\
                filter(Ingredient.meal_id == dp_item.meal_id).all()
        except NoRecordsError:
            logging.info('No materials found')
        except exc.SQLAlchemyError:
            logging.exception('Some problem occurred')

        # Step 4: Determine all materials with forecast and update them
        try:
            logging.info('Determine existing material forecasts ...')
            planned_materials = db.session.query(Material, Ingredient, Meal, MaterialForecast).\
                join(Material.referencedIn).\
                join(Material.referencedMaterialForecast).\
                join(Ingredient.meal).\
                filter(Ingredient.meal_id == dp_item.meal_id).\
                filter(MaterialForecast.plan_date == plan_date).\
                filter(MaterialForecast.inventory_id == login_session['default_inventory_id']).all()
        except NoRecordsError:
            logging.info('No existing material forecasts')
        except exc.SQLAlchemyError:
            logging.exception('Some problem occurred')

        print('# existing planned materials = ' + str(len(planned_materials)))

        for row in planned_materials:
            portions_factor = (float(dp_item.portions)/row.Meal.portions)
            # logging.info("portions_factor = " + str(portions_factor))
            # logging.info("Old MaterialForecast ("
                         # + str(row.Material.titleDE) + ") = "
                         # + str(row.MaterialForecast.quantity))
            row.MaterialForecast.quantity = row.MaterialForecast.quantity + portions_factor * row.Ingredient.quantity
            # logging.info("New MaterialForecast ("
                         # + str(row.Material.titleDE) + ") = "
                         # + str(row.MaterialForecast.quantity))

            # for materials with forecast remove the records from
            # the all material list
            for m in materials:
                if (m.Material.id == row.Material.id):
                    print('remove material from array')
                    materials.remove(m)

        session.commit()

        # Step 6: Create new forecast for all remaining materials in the
        # materials list
        for row in materials:
            portions_factor = (float(dp_item.portions)/row.Meal.portions)
            # logging.info("portions_factor = " + str(portions_factor))
            new_material_forecast = MaterialForecast(
                inventory_id=login_session['default_inventory_id'],
                material_id=row.Material.id,
                plan_date=plan_date,
                quantity=portions_factor * row.Ingredient.quantity,
                quantity_uom=row.Ingredient.uom_id
            )
            session.add(new_material_forecast)
        session.commit()


class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class NoRecordsError(Error):
    """Exception raised when an all() query does not return any results.

    Attributes:
        query -- the query that returned no values
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message



if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
