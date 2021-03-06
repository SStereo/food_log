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

# from datetime import datetime
import datetime

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
from huntingfood.models import Place, ShoppingOrder, ShoppingOrderItem

# Marshmallow Schemas
from huntingfood.models import \
    InventoryItemSchema, \
    MaterialForecastSchema, \
    MaterialSchema, \
    UOMSchema, \
    ShoppingOrderSchema, \
    ShoppingOrderItemSchema, \
    DietPlanItemSchema
from marshmallow import ValidationError


# CONSTANTS
INV_ITEM_CP_TYPE_NONE = 0
INV_ITEM_CP_TYPE_DAILY = 1
MAT_FORECAST_TYPE_CP = 1
MAT_FORECAST_TYPE_OP = 2


# Set Logging level
logger = logging.getLogger()
logger.setLevel(logging.INFO)
pp = pprint.PrettyPrinter(indent=1)

# TODO: not really required but just to ease the migration to flask-sqlalchemy
session = db.session

# db.create_all()
# db.session.commit()

# Create Marshmallow schema dumpers
inventory_items_schema = InventoryItemSchema(many=True)
inventory_item_schema = InventoryItemSchema()
diet_plan_items_schema = DietPlanItemSchema(many=True)
diet_plan_item_schema = DietPlanItemSchema()
shopping_orders_schema = ShoppingOrderSchema(many=True)
shopping_order_schema = ShoppingOrderSchema()
shopping_order_items_schema = ShoppingOrderItemSchema(many=True)
shopping_order_item_schema = ShoppingOrderItemSchema()
material_forecast_schema = MaterialForecastSchema(many=True)
material_schema = MaterialSchema(many=True)
uom_schema = UOMSchema(many=True)
uom_test_schema = UOMSchema()  # TODO:obsolete

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

nutrientDict = {}
uomDict = {}


@app.before_first_request
def initRefData():
    # TODO: Validate if there is a better way in sqlAlchemy ot achieve that
    # TODO: Ensure reload of dictionary when uom table changes
    logging.info('Caching nutrients ...')
    items = Nutrient.query
    for i in items:
        nutrientDict.update({i.titleEN: i.id})

    logging.info('Caching unit of measures ...')
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


# Custom static folder for node modules
@app.route('/node_modules/<path:filename>')
def node_static(filename):
    return send_from_directory(app.config['CUSTOM_STATIC_NODE_PATH'], filename)


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
    # TODO: Querying for the different plans and inventories really necessary?
    # TODO: Handle multiple inventories and shopping orders
    meals = Meal.query.filter_by(
        owner_id=login_session['user_id']).all()
    diet_plan = DietPlan.query.filter_by(
        id=login_session['default_diet_plan_id']).first()
    inventory = Inventory.query.filter_by(
        id=login_session['default_inventory_id']).first()
    shopping_order = ShoppingOrder.query.filter_by(
        status=1).first()

    logging.info('Diet Plan = %s' % login_session['default_diet_plan_id'])
    logging.info('Inventory = %s' % login_session['default_inventory_id'])

    return render_template(
        "shoppinglist.html",
        meals=meals,
        diet_plan=diet_plan,
        inventory=inventory,
        shopping_order=shopping_order,
        getIngredients=getIngredients,
        loginSession=login_session,  # TODO: is that necessary to pass it to the client?
        g_api_key=app.config['GOOGLE_API_KEY'])


# TODO: Obsolete
@app.route('/shoppinglist/items', methods=['GET', 'POST'])
def all_shopping_items_handler():

    inventory_items = []

    if request.method == 'POST':
        title = request.form.get('title')
        inventory_item = InventoryItem(title=title, level=0)
        session.add(inventory_item)
        session.commit()
        inventory_items.append(inventory_item)
        return jsonify(inventory_items=[i.serialize for i in inventory_items])

    elif request.method == 'GET':
        inventory_items = InventoryItem.query.all()
        # TODO: return nested structures including inventory header and user
        # information with https://flask-marshmallow.readthedocs.io/en/latest/
        return jsonify(inventory_items=[i.serialize for i in inventory_items])


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
        logging.info("Start file handler")
        # ---- FILE HANDLING -----
        filename = ""
        if 'file' not in request.files:
            logging.info("file not in request.files")
            # TODO: Implement flash messages
            # flash('No file part')

            return redirect(request.url)

        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            # TODO: Implement flash
            # flash('No selected file')
            logging.info("Filename == ''")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            now = datetime.datetime.now()
            filename = "%s.%s" % (now.strftime("%Y-%m-%d-%H-%M-%S-%f"), filename.rsplit('.', 1)[1])  #$s replaced by timestamp and file extension
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], "%s.%s" % (now.strftime("%Y-%m-%d-%H-%M-%S-%f"), file.filename.rsplit('.', 1)[1]))
            logging.info("filepath = " + filepath)
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

            material = createMaterial(ingredient_text, user_language, ingredient_uom)

            logging.info('Material created (len %s): %s' % (len(material.titleEN), material.titleEN))

            # Identify food entity from entered text using language processing
            # use en language to improve results since en splits combined
            # german words
            food_entity = analyze_ingredient(
                material.titleEN, language='en')
            logging.info("Food entity: %s" % food_entity)

            # TODO:  Handle long strings exceeding 80 characters
            # Add new ingredient into database
            newIngredient = Ingredient(quantity=request.form['quantity'+row],
                                       uom_id=ingredient_uom,
                                       meal_id=newMeal.id,
                                       title=ingredient_text,
                                       titleEN=material.titleEN,
                                       base_food_part=food_entity,
                                       material_id=material.id)

            session.add(newIngredient)
            session.commit()

            x += 1

        return redirect(url_for("showMeals"))

    elif request.method == 'POST' and request.form['button'] == "Cancel":
        logging.info("Request cancelled")
        meals = Meal.query
        return render_template("meals.html", meals=meals, getIngredients=getIngredients)
    else:  # 'GET':
        uoms = UOM.query
        materials = Material.query
        return render_template("meals_add.html", uoms=uoms, materials=materials)


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


def createMaterial(title_local_lang, local_lang_code, uom_base_id):

    # Step 1: Translate from local language to EN
    if (local_lang_code != 'en'):
        translation = translate_client.translate(
            title_local_lang, source_language=local_lang_code)
        title_EN = translation['translatedText']
        logging.info("New Material translation. title(%s) = %s -> title(en) = %s" % (local_lang_code, title_local_lang, title_EN))
    else:
        title_EN = title_local_lang

    # Query a food database (e.g. NDB) to retrieve nutrient information
    # and to create a food master data record. The id of such a record
    # is returned if a match in the food database was found.
    material = createFoodviaNDB(title_EN, title_local_lang, local_lang_code, uom_base_id)

    # not a known Food in NDB
    if not material:
        material = Material(
            titleEN=title_EN,
            title=title_local_lang,
            language_code=local_lang_code,
            uom_base_id=uom_base_id)
        session.add(material)
        session.commit()

    return material


# Food database helper functions
# TODO: Rework material creation
def createFoodviaNDB(keyword,
                     keyword_local_language,
                     local_language_code,
                     base_uom):

    if app.config['NDB_KEY']:
        n = ndb.NDB(app.config['NDB_KEY'])
        results = n.search_keyword(keyword)
        if results:

            i = list(results['items'])[0]  # TODO: identify relevant item, for now take the first one
            logging.info("Found NDB item: "+i.get_name())

            # Create Food Main Group
            foodMainGroup = FoodMainGroup.query.filter_by(titleEN=i.get_group()).first()
            if not foodMainGroup:
                logging.info('Create FoodMainGroup: ' + i.get_group())
                foodMainGroup = FoodMainGroup(titleEN=i.get_group())
                session.add(foodMainGroup)
                session.commit()

            # Create Food
            name_truncated_80 = (i.get_name()[:75] + '..') if len(i.get_name()) > 75 else i.get_name()
            logging.info('Create Material (len %s): %s' % (len(name_truncated_80), name_truncated_80))
            food = Material.query.filter_by(titleEN=keyword).first()
            if not food:
                food = Material(
                    ndb_title=name_truncated_80,
                    titleEN=keyword,
                    title=keyword_local_language,
                    language_code=local_language_code,
                    uom_base_id=base_uom,
                    ndb_code=i.get_ndbno(),
                    food_maingroup_id=foodMainGroup.id)
                session.add(food)
                session.commit()

                # Create Nutrients
                report = n.food_report(i.get_ndbno())

                nutrients = report['food'].get_nutrients()
                food_compositions = []
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
                                               title=translated_text)
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
                    food_compositions.append(
                        FoodComposition(material_id=food.id,
                                        nutrient_id=nutriendID,
                                        per_qty_uom=uomID,
                                        per_qty=100,
                                        value=n.get_value()
                                        )
                                            )

                session.add_all(food_compositions)
                session.commit()
            return food
        else:
            logging.info("No results in NDB found")
            return None
    else:
        logging.info("Missing API Key in Environment Variable")
        return None


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# API Endpoints
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@app.route('/api/v1/meals', methods=['GET'])
def api_v1_meals():
    if request.method == 'GET':
        meals = Meal.query.filter_by(owner_id=login_session['user_id']).all()
        return jsonify(meals=[m.serialize for m in meals])


@app.route('/api/v1/uom', methods=['GET'])
def api_v1_uom():
    uoms = []
    if request.method == 'GET':
        type = request.args.get('type')
        if type:
            uoms = UOM.query.filter_by(
                type=type).all()
        else:
            uoms = UOM.query.all()
        result = uom_schema.dump(uoms).data
        return jsonify({'uoms': result})


@app.route('/api/v1/materials', methods=['GET'])
def api_v1_materials():
    materials = []
    if request.method == 'GET':
        search_term = request.args.get('query')
        if search_term:
            materials = Material.query.filter(Material.title.like('%' + search_term + '%')).all()
        else:
            materials = Material.query.all()
        result = material_schema.dump(materials).data
        #  return jsonify({'materials': result})
        return jsonify(result)


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
        result = diet_plan_items_schema.dump(dp_items).data
        return jsonify({'diet_plan_items': result})

    if request.method == 'POST':

        json_data = request.get_json()
        if not json_data:
            return jsonify({'message': 'No input data provided'}), 400
        try:
            data, errors = diet_plan_item_schema.load(json_data)
        except ValidationError as err:
            return jsonify(err.messages), 422

        # TODO: Improve to avoid dict are created during schema.load and an
        # object is created instead
        # https://github.com/marshmallow-code/marshmallow-sqlalchemy/issues/47
        # plan_date = data.plan_date
        # meal_id = data.meal.id
        # portions = data.portions
        # material_id = data.material.id if data.material else None
        # consumed = data.consumed

        plan_date = data['plan_date']
        meal_id = data['meal'].id
        portions = data['portions']

        # Validations
        if (not portions):
            message = 'api_v1_dietplan: POST | Missing field: portions.'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response

        if (not plan_date):
            message = 'api_v1_dietplan: POST | Missing field: plan_date.'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response

        if (not meal_id):
            message = 'api_v1_dietplan: POST | Missing field: meal.'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response

        # Step 1: Create DIET PLAN ITEM
        diet_plan_item = DietPlanItem(
            diet_plan_id=diet_plan_id,
            plan_date=plan_date,
            meal_id=meal_id,
            portions=portions
            )
        session.add(diet_plan_item)
        session.commit()

        update_material_forecast_dp(diet_plan_id, login_session['default_inventory_id'], plan_date)

        # Step 2: Return Response
        result = diet_plan_item_schema.dump(diet_plan_item).data
        return jsonify({'diet_plan_item': result}), 201

    if request.method == 'PUT':
        json_data = request.get_json()
        if not json_data:
            return jsonify({'message': 'No input data provided'}), 400
        try:
            data, errors = diet_plan_item_schema.load(json_data)
        except ValidationError as err:
            return jsonify(err.messages), 422

        id = data.id
        plan_date = data.plan_date
        meal_id = data.meal.id
        portions = data.portions
        material_id = data.material.id if data.material else None
        consumed = data.consumed

        print('id = ' + str(id))

        diet_plan_item = DietPlanItem.query.filter_by(id=id).one_or_none()

        if (not diet_plan_item):
            message = 'api_v1_dietplan: PUT | Diet Plan Item not found.'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response

        dp_plan_date = diet_plan_item.plan_date
        if (plan_date != dp_plan_date):
            message = 'api_v1_dietplan: PUT | Change not allowed for field: plan_date.'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response

        # Validations
        if (not portions):
            message = 'api_v1_dietplan: PUT | Missing field: portions.'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response

        if (not plan_date):
            message = 'api_v1_dietplan: PUT | Missing field: plan_date.'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response

        if (not meal_id):
            message = 'api_v1_dietplan: PUT | Missing field: meal.'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response

        diet_plan_item.meal_id = meal_id
        diet_plan_item.consumed = consumed
        diet_plan_item.portions = portions
        diet_plan_item.material_id = material_id
        session.commit()

        update_material_forecast_dp(diet_plan_id, login_session['default_inventory_id'], plan_date)

        result = diet_plan_item_schema.dump(diet_plan_item).data
        return jsonify({'diet_plan_item': result})

    if request.method == 'DELETE':
        json_data = request.get_json()
        if not json_data:
            return jsonify({'message': 'No input data provided'}), 400
        try:
            data, errors = diet_plan_item_schema.load(json_data)
        except ValidationError as err:
            return jsonify(err.messages), 422

        id = data.id
        diet_plan_item = DietPlanItem.query.filter_by(id=id).one_or_none()

        if (not id):
            message = 'api_v1_dietplan: DELETE | Missing field: id'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response

        if (not diet_plan_item):
            message = 'api_v1_dietplan: DELETE | dietplan item with id = %s does not exist' % id
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response

        plan_date = diet_plan_item.plan_date
        session.delete(diet_plan_item)
        session.commit()

        update_material_forecast_dp(diet_plan_id, login_session['default_inventory_id'], plan_date)

        message = 'api_v1_dietplan: DELETE | Item successfully deleted'
        response = make_response(json.dumps(
            message), 204)
        response.headers['Content-Type'] = 'application/json'
        logging.info(message)
        return response


@app.route('/api/v1/inventory/<int:inventory_id>', methods=['GET', 'POST', 'DELETE', 'PUT'])
def api_v1_inventory(inventory_id):
    inventory_items = []

    if request.method == 'GET':
        inventory_items = InventoryItem.query.filter_by(
            inventory_id=inventory_id).all()
        result = inventory_items_schema.dump(inventory_items).data
        return jsonify({'inventory_items': result})

    if request.method == 'POST':
        json_data = request.get_json()
        if not json_data:
            return jsonify({'message': 'No input data provided'}), 400
        try:
            data, errors = inventory_item_schema.load(json_data)
        except ValidationError as err:
            return jsonify(err.messages), 422

        # TODO: If the client does not send the field in the json file
        # it will lead into a key error when reading the dict, fix this overall
        # perhaps validations in marshmallow is the answer
        title = data['title']
        material_id = data['material'].id if data['material'] else None

        # Validations
        if (not title) and (not material_id):
            message = 'api_v1_inventory: POST | Missing field: title.'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response

        # New Material
        elif (title) and (not material_id):
            uom_base = data['uom_base'].uom
            uom_stock = data['uom_stock'].uom
            quantity_conversion_factor = data['quantity_conversion_factor']

            if (not uom_base):
                message = 'api_v1_inventory: POST | Missing field: uom_base.'
                response = make_response(json.dumps(
                    message), 400)
                response.headers['Content-Type'] = 'application/json'
                logging.warning(message)
                return response
            if (not uom_stock):
                message = 'api_v1_inventory: POST | Missing field: uom_stock.'
                response = make_response(json.dumps(
                    message), 400)
                response.headers['Content-Type'] = 'application/json'
                logging.warning(message)
                return response

            message = 'api_v1_inventory: POST | No existing material. Creating new material ...'
            logging.info(message)
            material = createMaterial(title, login_session['language'], uom_base)
            material_id = material.id

        # Existing Material
        elif (not title) and (material_id):
            message = 'api_v1_inventory: POST | Existing material.'
            logging.info(message)
            material = Material.query.filter_by(id=material_id).one_or_none()
            inventory_item = InventoryItem.query.filter_by(
                material_id=material_id,
                inventory_id=inventory_id).one_or_none()
            # Use title from existing material
            if (material):
                title = material.title
                uom_base = material.uom_base_id
                uom_stock = material.uom_stock_id
                quantity_conversion_factor = material.default_base_units_per_stock_unit
                if (inventory_item):
                    message = 'api_v1_inventory: POST | Inventory Item relating to material %s does already exist.' % material_id
                    response = make_response(json.dumps(
                        message), 200)
                    response.headers['Content-Type'] = 'application/json'
                    logging.info(message)
                    return response
            else:
                message = 'api_v1_inventory: POST | Material with id %s not found.' % material_id
                response = make_response(json.dumps(
                    message), 400)
                response.headers['Content-Type'] = 'application/json'
                logging.warning(message)
                return response

        # Step 1: Create an inventory item
        inventory_item = InventoryItem(
            inventory_id=inventory_id,
            titleEN=material.titleEN,
            title=title,
            material_id=material_id,
            uom_stock_id=uom_stock,
            uom_base_id=uom_base,
            quantity_conversion_factor=quantity_conversion_factor,
            )
        session.add(inventory_item)
        session.commit()

        result = inventory_item_schema.dump(inventory_item).data
        return jsonify({'inventory_item': result}), 201

    if request.method == 'PUT':

        json_data = request.get_json()
        if not json_data:
            return jsonify({'message': 'No input data provided'}), 400
        try:
            data, errors = inventory_item_schema.load(json_data)
        except ValidationError as err:
            return jsonify(err.messages), 422

        # TODO: find a way to catch cases where field is not provided
        # so the key is missing. This can happen when the ajax call on the
        # client is asked to send a undefined variable and then omits the value
        id = data['id']
        title = data['title']
        quantity_base = data['quantity_base'] if 'quantity_base' in data.keys() else None
        quantity_stock = data['quantity_stock'] if 'quantity_stock' in data.keys() else None
        quantity_conversion_factor = data['quantity_conversion_factor']
        uom_base = data['uom_base'].uom if data['uom_base'] else None
        uom_stock = data['uom_stock'].uom if data['uom_stock'] else None
        material_id = data['material'].id if data['material'] else None
        re_order_level = data['re_order_level']
        re_order_quantity = data['re_order_quantity'] if 're_order_quantity' in data.keys() else None
        ignore_forecast = data['ignore_forecast']

        # consumption plan fields
        cp_type = data['cp_type']
        cp_quantity = data['cp_quantity'] if 'cp_quantity' in data.keys() else None
        cp_plan_date_start = data['cp_plan_date_start']
        cp_plan_date_end = data['cp_plan_date_end']
        cp_period = data['cp_period']

        # Other plan fields
        op_plan_date_start = data['op_plan_date_start']
        op_plan_date_end = data['op_plan_date_end']
        op_quantity = data['op_quantity'] if 'op_quantity' in data.keys() else None

        # Validations
        if (not id):
            message = 'api_v1_inventory: PUT | Missing field: id.'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response

        if (not material_id):
            message = 'api_v1_inventory: PUT | Missing field: material_id.'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response

        if (cp_type > INV_ITEM_CP_TYPE_NONE) and (cp_quantity is None):
            message = 'api_v1_inventory: PUT | Missing field: cp_quantity.'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response

        # TODO: Create a consistent behaviour for querying the db, with or without try?
        inventory_item = InventoryItem.query.filter_by(id=id).one_or_none()
        if (not inventory_item):
            message = 'api_v1_inventory: PUT | No inventory item found.'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response

        # Step 1: Update inventory item
        cp_changed = False
        op_changed = False
        inventory_item.title = title,
        inventory_item.material_id = material_id,
        inventory_item.quantity_base = quantity_base,
        inventory_item.quantity_stock = quantity_stock,
        inventory_item.quantity_conversion_factor = quantity_conversion_factor,
        inventory_item.uom_base_id = uom_base,
        inventory_item.uom_stock_id = uom_stock,
        inventory_item.re_order_level = re_order_level,
        inventory_item.re_order_quantity = re_order_quantity
        inventory_item.ignore_forecast = ignore_forecast

        # Identify if cp was changed
        if (inventory_item.cp_type != cp_type) \
                or (inventory_item.cp_quantity != cp_quantity) \
                or (inventory_item.cp_plan_date_start != cp_plan_date_start) \
                or (inventory_item.cp_period != cp_period) \
                or (inventory_item.cp_plan_date_end != cp_plan_date_end):
            cp_changed = True
            inventory_item.cp_type = cp_type,
            inventory_item.cp_quantity = cp_quantity,
            inventory_item.cp_plan_date_start = cp_plan_date_start,
            inventory_item.cp_period = cp_period,
            inventory_item.cp_plan_date_end = cp_plan_date_end

        # Identify if op was changed
        if (inventory_item.op_plan_date_start != op_plan_date_start) \
                or (inventory_item.op_plan_date_end != op_plan_date_end) \
                or (inventory_item.op_quantity != op_quantity):
            op_changed = True
            inventory_item.op_plan_date_start = op_plan_date_start,
            inventory_item.op_plan_date_end = op_plan_date_end,
            inventory_item.op_quantity = op_quantity,
        session.commit()
        logging.info('Inventory Item %s successfully updated' % inventory_item.id)

        # Step 2: update material forecasts if changed
        if (cp_changed):
            update_material_forecast_cp(inventory_item)

        if (op_changed):
            update_material_forecast_op(inventory_item)

        # Step 3: return modified items
        inventory_items = InventoryItem.query.filter_by(
            id=inventory_item.id).all()
        result = inventory_items_schema.dump(inventory_items).data
        return jsonify({'inventory_items': result})

    if request.method == 'DELETE':
        json_data = request.get_json()
        if not json_data:
            return jsonify({'message': 'No input data provided'}), 400
        try:
            data, errors = inventory_item_schema.load(json_data)
        except ValidationError as err:
            return jsonify(err.messages), 422

        id = data['id']

        inventory_item = InventoryItem.query.filter_by(id=id).one_or_none()

        if (id) and (inventory_item):
            session.delete(inventory_item)
            session.commit()
            message = 'api_v1_inventory: DELETE | Item successfully deleted'
            response = make_response(json.dumps(
                message), 204)
            response.headers['Content-Type'] = 'application/json'
            logging.info(message)
            return response
        else:
            message = 'api_v1_inventory: DELETE | Can not delete item because item was not found'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response


@app.route('/api/v1/shopping_order/<int:shopping_order_id>', methods=['GET', 'DELETE', 'PUT'])
@app.route('/api/v1/shopping_order', methods=['GET', 'POST'])
def api_v1_shopping_order(shopping_order_id=None):
    shopping_orders = []

    if request.method == 'GET':

        status = request.args.get('status')

        # TODO: add creator_id=login_session['user_id']
        if shopping_order_id is not None:
            shopping_orders = ShoppingOrder.query.filter_by(
                shopping_order_id=shopping_order_id).first()
            result = shopping_order_schema.dump(shopping_orders).data
        elif status:
            shopping_orders = ShoppingOrder.query.filter_by(
                status=status).all()
            result = shopping_orders_schema.dump(shopping_orders).data
        else:
            shopping_orders = ShoppingOrder.query.all()
            result = shopping_orders_schema.dump(shopping_orders).data

        if shopping_orders:
            return jsonify({'shopping_orders': result})
        else:
            response = make_response(json.dumps(
                'Resource not found'), 404)
            response.headers['Content-Type'] = 'application/json'
            return response

    if request.method == 'POST':

        json_data = request.get_json()
        if not json_data:
            return jsonify({'message': 'No input data provided'}), 400
        try:
            data, errors = shopping_order_schema.load(json_data)
        except ValidationError as err:
            return jsonify(err.messages), 422

        type = data['type']
        status = data['status']
        plan_forecast_days = data['plan_forecast_days']

        # Validations
        if (not type):
            message = 'api_v1_shopping_order: POST | Missing field: type.'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response
        elif (not status):
            message = 'api_v1_shopping_order: POST | Missing field: status.'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response
        elif (not plan_forecast_days):
            message = 'api_v1_shopping_order: POST | Missing field: plan_forecast_days.'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response

        # Step 1: Create a shopping order
        shopping_order = ShoppingOrder(
            type=type,
            status=status,
            plan_forecast_days=plan_forecast_days,
            creator_id=login_session['user_id']
            )
        session.add(shopping_order)
        session.commit()

        result = shopping_order_schema.dump(shopping_order).data
        return jsonify({'shopping_order': result}), 201

    if request.method == 'PUT':

        json_data = request.get_json()
        if not json_data:
            return jsonify({'message': 'No input data provided'}), 400
        try:
            data, errors = shopping_order_schema.load(json_data)
        except ValidationError as err:
            return jsonify(err.messages), 422

        shopping_order = data

        # Validations
        if (not shopping_order_id):
            message = 'api_v1_shopping_order: POST | Missing field: shopping_order_id.'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response

        # TODO: Identify if the given id is valid and an existing object was found or not
        # otherwise marshmallow is creating a new object which we do not want.
        # https://github.com/marshmallow-code/marshmallow-sqlalchemy/issues/50

        if (not shopping_order):
            message = 'api_v1_shopping_order: PUT | No shopping order found.'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response

        if (not shopping_order.type):
            message = 'api_v1_shopping_order: POST | Missing field: type.'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response

        if (not shopping_order.status):
            message = 'api_v1_shopping_order: POST | Missing field: status.'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response

        if (not shopping_order.plan_forecast_days):
            message = 'api_v1_shopping_order: POST | Missing field: plan_forecast_days.'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response

        # In case of a status change from 1 to 2 (closing order)
        if (shopping_order.status == 2) and (shopping_order.closed is None):
            shopping_order.closed = datetime.datetime.utcnow()

            # Update quantities on inventory items with the purchased quantity
            for inv, item in session.query(InventoryItem, ShoppingOrderItem).filter(InventoryItem.material_id == ShoppingOrderItem.material_id).filter(ShoppingOrderItem.shopping_order_id == shopping_order_id).all():
                inv.quantity_base = inv.quantity_base + item.quantity_purchased
                session.add(inv)

        session.commit()

        result = shopping_order_schema.dump(shopping_order).data
        return jsonify({'shopping_order': result})


@app.route('/api/v1/shopping_order_item/<int:shopping_order_item_id>', methods=['GET', 'DELETE', 'PUT'])
@app.route('/api/v1/shopping_order_item', methods=['POST'])
def api_v1_shopping_order_item(shopping_order_item_id=None):
    shopping_order_items = []

    if request.method == 'POST':

        json_data = request.get_json()
        if not json_data:
            return jsonify({'message': 'No input data provided'}), 400
        try:
            data, errors = shopping_order_item_schema.load(json_data)
        except ValidationError as err:
            return jsonify(err.messages), 422

        id = data['id'] if 'id' in data.keys() else None
        material_id = data['material'].id
        shopping_order_id = data['shopping_order'].id
        quantity_purchased = data['quantity_purchased']
        in_basket = data['in_basket']
        in_basket_time = data['in_basket_time']
        in_basket_geo_lon = data['in_basket_geo_lon']
        in_basket_geo_lat = data['in_basket_geo_lat']

        # Validations
        if (id):
            shopping_order_item = ShoppingOrderItem.query.filter_by(id=shopping_order_id).one_or_none()
            if shopping_order_item:
                message = 'api_v1_shopping_order_item: POST | Object already exist.'
                response = make_response(json.dumps(
                    message), 400)
                response.headers['Content-Type'] = 'application/json'
                logging.warning(message)
                return response

        if (not material_id):
            message = 'api_v1_shopping_order_item: POST | Missing field: material_id.'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response
        elif (not shopping_order_id):
            message = 'api_v1_shopping_order_item: POST | Missing field: shopping_order_id.'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response

        # TODO: Validate if item already exists (material, inventory combination, plan_date)
        # DO WE NEED TO RELATE SHOPPING ORDER ITEM to a INVENTORY ITEM via id directly?

        # Step 1: Create a shopping order
        shopping_order_item = ShoppingOrderItem(
            inventory_id=login_session['default_inventory_id'],
            material_id=material_id,
            shopping_order_id=shopping_order_id,
            quantity_purchased=quantity_purchased,
            in_basket=in_basket,
            in_basket_time=in_basket_time,
            in_basket_geo_lon=in_basket_geo_lon,
            in_basket_geo_lat=in_basket_geo_lat,
            )
        session.add(shopping_order_item)
        session.commit()

        result = shopping_order_item_schema.dump(shopping_order_item).data
        return jsonify({'shopping_order_item': result}), 201

    if request.method == 'PUT':

        json_data = request.get_json()
        if not json_data:
            return jsonify({'message': 'No input data provided'}), 400
        try:
            data, errors = shopping_order_item_schema.load(json_data)
        except ValidationError as err:
            return jsonify(err.messages), 422

        id = shopping_order_item_id
        material_id = data.material.id
        shopping_order_id = data.shopping_order.id
        quantity_purchased = data.quantity_purchased
        in_basket = data.in_basket
        in_basket_time = data.in_basket_time
        in_basket_geo_lon = data.in_basket_geo_lon
        in_basket_geo_lat = data.in_basket_geo_lat

        # Validations
        if (not material_id):
            message = 'api_v1_shopping_order_item: PUT | Missing field: material_id.'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response
        elif (not shopping_order_id):
            message = 'api_v1_shopping_order_item: PUT | Missing field: shopping_order_id.'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response

        # TODO: Create a consistent behaviour for querying the db, with or without try?
        shopping_order_item = ShoppingOrderItem.query.filter_by(id=id).one_or_none()
        if (not shopping_order_item):
            message = 'api_v1_shopping_order_item: PUT | Shopping order item not found.'
            response = make_response(json.dumps(
                message), 400)
            response.headers['Content-Type'] = 'application/json'
            logging.warning(message)
            return response

        shopping_order_item.material_id = material_id
        shopping_order_item.quantity_purchased = quantity_purchased
        shopping_order_item.in_basket = in_basket
        shopping_order_item.in_basket_time = in_basket_time
        shopping_order_item.in_basket_geo_lon = in_basket_geo_lon
        shopping_order_item.in_basket_geo_lat = in_basket_geo_lat

        session.commit()

        result = shopping_order_item_schema.dump(shopping_order_item).data
        return jsonify({'shopping_order_item': result})


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
    logging.info("content: %s" % content)
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
            logging.info(u'{} - {}: {} - {} - {}'.format(index,pos_tag[token.part_of_speech.tag],token.text.content,token.dependency_edge.head_token_index,parse_label[token.dependency_edge.label]))
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
# 3) Combine with regular and other consumption updates
def update_material_forecast_dp(inventory_id, diet_plan_id, plan_date):

    # Step 1: Delete all forecasts for the given plan date and inventory
    # TODO: It assumes that diet plan entries are allways only one day long
    try:
        logging.info('DELETE all Forecasts ...')
        forecasts = db.session.query(MaterialForecast).\
            filter(MaterialForecast.inventory_id == inventory_id).\
            filter(MaterialForecast.plan_date_start == plan_date).\
            filter(MaterialForecast.type == 0).\
            delete(synchronize_session=False)
    except NoRecordsError:
        logging.info('No existing material forecasts')
    except exc.SQLAlchemyError:
        logging.exception('Some problem occurred during deletion of MaterialForecasts')

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
            inv_items_user_subquery = InventoryItem.query.\
                select_from(InventoryItem).\
                filter(InventoryItem.inventory_id == login_session['default_inventory_id']).subquery()

            missing_inventory_items = Material.query.\
                select_from(Material).\
                outerjoin(Material.referencedIn).\
                outerjoin(inv_items_user_subquery, Material.id == inv_items_user_subquery.c.material_id).\
                filter(Ingredient.meal_id == dp_item.meal_id).\
                filter(inv_items_user_subquery.c.material_id == None).all()
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
                    title=inv_item.title,
                    material_id=inv_item.id,
                    quantity_stock=0,
                    quantity_base=0,
                    uom_base_id=inv_item.uom_base_id,
                    uom_stock_id=inv_item.uom_stock_id,
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
                filter(MaterialForecast.plan_date_start == plan_date).\
                filter(MaterialForecast.type == 0).\
                filter(MaterialForecast.inventory_id == login_session['default_inventory_id']).all()
        except NoRecordsError:
            logging.info('No existing material forecasts')
        except exc.SQLAlchemyError:
            logging.exception('Some problem occurred')

        for row in planned_materials:
            portions_factor = (float(dp_item.portions)/row.Meal.portions)
            logging.info("portions_factor = " + str(portions_factor))
            logging.info("Old MaterialForecast ("
                         + str(row.Material.title) + ") = "
                         + str(row.MaterialForecast.quantity_per_day))
            row.MaterialForecast.quantity_per_day = row.MaterialForecast.quantity_per_day + portions_factor * row.Ingredient.quantity
            logging.info("New MaterialForecast ("
                         + str(row.Material.title) + ") = "
                         + str(row.MaterialForecast.quantity_per_day))

            # for materials with forecast remove the records from
            # the all material list
            for m in materials:
                if (m.Material.id == row.Material.id):
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
                type=0,
                plan_date_start=plan_date,
                plan_date_end=(plan_date + datetime.timedelta(days=1)),
                quantity_per_day=portions_factor * row.Ingredient.quantity,
                quantity_uom=row.Ingredient.uom_id
            )
            session.add(new_material_forecast)
        session.commit()


# TODO: Combine with op function
def update_material_forecast_cp(inventory_item):

    # Step 1: Delete existing forecast
    logging.info('Delete consumption forecast due to change ...')
    forecasts = db.session.query(MaterialForecast).\
        filter(MaterialForecast.inventory_id == inventory_item.inventory_id).\
        filter(MaterialForecast.material_id == inventory_item.material_id).\
        filter(MaterialForecast.type == MAT_FORECAST_TYPE_CP).\
        delete(synchronize_session=False)
    session.commit()

    if (inventory_item.cp_type == INV_ITEM_CP_TYPE_DAILY):

        logging.info('Create new forecasts for daily consumption ...')
        plan_date_start = inventory_item.cp_plan_date_start
        # TODO: Wire up plan_date_end to the front end
        plan_date_end = plan_date_start + datetime.timedelta(days=3650)
        new_forecast = MaterialForecast(
                    inventory_id=inventory_item.inventory_id,
                    material_id=inventory_item.material_id,
                    type=MAT_FORECAST_TYPE_CP,
                    plan_date_start=plan_date_start,
                    plan_date_end=plan_date_end,
                    quantity_per_day=inventory_item.cp_quantity,
                    quantity_uom=inventory_item.uom_base_id)
        session.add(new_forecast)
        session.commit()

    if (inventory_item.cp_type == INV_ITEM_CP_TYPE_NONE):
        logging.info('Forecast for consumption plan has been deleted.')


def update_material_forecast_op(inventory_item):

    logging.info('Delete other forecast due to change ...')
    forecasts = db.session.query(MaterialForecast).\
        filter(MaterialForecast.inventory_id == inventory_item.inventory_id).\
        filter(MaterialForecast.material_id == inventory_item.material_id).\
        filter(MaterialForecast.type == MAT_FORECAST_TYPE_OP).\
        delete(synchronize_session=False)
    session.commit()

    if (inventory_item.op_quantity > 0):

        logging.info('Create new forecast for other consumption ...')
        new_forecast = MaterialForecast(
                    inventory_id=inventory_item.inventory_id,
                    material_id=inventory_item.material_id,
                    type=MAT_FORECAST_TYPE_OP,
                    plan_date_start=inventory_item.op_plan_date_start,
                    plan_date_end=inventory_item.op_plan_date_end,
                    quantity=inventory_item.op_quantity,
                    quantity_uom=inventory_item.uom_base_id)
        session.add(new_forecast)
        session.commit()

    else:
        logging.info('Forecast for other consumption has been deleted.')


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
