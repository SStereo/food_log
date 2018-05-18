from huntingfood import db

# password encryption into hash
from passlib.apps import custom_app_context as pwd_context

# libraries for token generation
import random
import string
import datetime
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature,
                          SignatureExpired)

# secret key required for encrypting a token
secret_key = ''.join(
    random.choice(
        string.ascii_uppercase + string.digits) for x in range(32))


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    picture = db.Column(db.String(250), nullable=True)
    provider = db.Column(db.String(20), nullable=True)
    provider_id = db.Column(db.String(120), nullable=True)
    active = db.Column(db.Boolean(), default=True)
    confirmed_at = db.Column(db.DateTime())
    password_hash = db.Column(db.String(255))
    language = db.Column(db.String(6), nullable=False)
    default_diet_plan_id = db.Column(db.Integer, db.ForeignKey('diet_plans.id'), nullable=True, unique=True)  # TODO: fix this when multiple users share one diet_plan and inventory
    default_inventory_id = db.Column(db.Integer, db.ForeignKey('inventories.id'), nullable=True, unique=True)
    default_portions = db.Column(db.SmallInteger, nullable = True)
    street = db.Column(db.String(120), nullable=True)
    city = db.Column(db.String(120), nullable=True)
    state = db.Column(db.String(120), nullable=True)
    zip = db.Column(db.String(120), nullable=True)

    groups = db.relationship("UserGroupAssociation", back_populates="user")
    meals = db.relationship("Meal", cascade="all, delete-orphan", back_populates="owner")
    inventories = db.relationship("Inventory", primaryjoin='User.id == Inventory.creator_id', cascade="all, delete-orphan")
    diet_plans = db.relationship("DietPlan", primaryjoin='User.id == DietPlan.creator_id', cascade="all, delete-orphan", back_populates="creator")
    default_diet_plan = db.relationship("DietPlan", primaryjoin='User.default_diet_plan_id == DietPlan.id', cascade="all, delete-orphan", single_parent=True)
    default_inventory = db.relationship("Inventory", primaryjoin='User.default_inventory_id == Inventory.id', cascade="all, delete-orphan", single_parent=True)
    shopping_order = db.relationship("ShoppingOrder", cascade="all, delete-orphan")

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration):
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})

    # defines how to print objects. Is good for debugging
    def __repr__(self):
        return '<User {}>'.format(self.name)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
            return str(self.id)


class UserGroupAssociation(db.Model):
    __tablename__ = 'user_group_association'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    user_group_id = db.Column(db.Integer, db.ForeignKey('user_groups.id'), primary_key=True)
    is_owner = db.Column(db.Boolean, unique = False, default = False)

    group = db.relationship("UserGroup", back_populates="users")
    user = db.relationship("User", back_populates="groups")


# Required to provide access for the whole family on shopping lists
# Every user gets their own group unless their are added to another Group
# For now a user can only be in one group/family
class UserGroup(db.Model):
    __tablename__ = 'user_groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    # owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # owner_id = db.Column(db.Integer, nullable=False)
    # fk_owner = db.ForeignKeyConstraint(['users.id'], ['owner_id'])
    picture = db.Column(db.String(250), nullable=True)

    users = db.relationship("UserGroupAssociation", back_populates="group")

    # owner = db.relationship("User", foreign_keys=[owner_id], post_update=True)


class UOM(db.Model):
    __tablename__ = 'units_of_measures'
    uom = db.Column(db.String(length=5, convert_unicode=True), primary_key = True)
    longEN = db.Column(db.String(80), nullable = True)
    shortDE = db.Column(db.String(5), nullable = True)
    longDE = db.Column(db.String(80), nullable = True)
    type = db.Column(db.String(1), nullable = True) # 1 = ingredients only, 2 = both, 3 = nutrients only


class Meal(db.Model):
    __tablename__ = 'meals'
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(80), nullable = False)
    description = db.Column(db.String(250), nullable = True)
    portions = db.Column(db.SmallInteger, nullable = True)
    calories = db.Column(db.String(20), nullable = True)
    rating = db.Column(db.SmallInteger, nullable = True)
    image = db.Column(db.String, nullable = True)
    created = db.Column(db.DateTime, default = datetime.datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    user_group_id = db.Column(db.Integer, db.ForeignKey('user_groups.id'))

    owner = db.relationship("User", back_populates="meals", foreign_keys=[owner_id])
    user_group = db.relationship("UserGroup")
    ingredients = db.relationship("Ingredient", back_populates="meal", cascade="all, delete-orphan")
    diet_plans = db.relationship("DietPlanItem", back_populates="meal", cascade="all, delete-orphan")

    @property
    def serialize(self):
        #Returns object data in easily serializable format
        return {
            'id' : self.id,
            'title' : self.title,
            'description' : self.description,
            'portions' : self.portions,
            'rating' : self.rating,
            'image' : self.image,
            'created' : self.created,
        }


class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    id = db.Column(db.Integer, primary_key = True)
    quantity = db.Column(db.Float, nullable = False)
    uom_id = db.Column(db.String(5), db.ForeignKey('units_of_measures.uom'), nullable = False)
    meal_id = db.Column(db.Integer, db.ForeignKey('meals.id'), nullable = False, index = True)
    title = db.Column(db.String(80), nullable = False) #gehackte Dosentomaten
    titleEN = db.Column(db.String(80), nullable = True) #chopped canned tomatoes
    processing_part = db.Column(db.String(80), nullable = True) # chopped canned
    preparation_part = db.Column(db.String(80), nullable = True) # empty
    base_food_part = db.Column(db.String(80), nullable = True) # Tomatoe

    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable = True, index = True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    material = db.relationship("Material")
    meal = db.relationship("Meal", back_populates="ingredients")
    uom = db.relationship("UOM")


# based on german classification system BLS (Bundeslebensmittelschlüssel)
# consider integrating directly using a server license https://www.blsdb.de/license


class FoodMainGroup(db.Model):
    __tablename__ = 'food_maingroup'
    id = db.Column(db.Integer, primary_key = True)
    titleEN = db.Column(db.String(80), nullable = False)
    titleDE = db.Column(db.String(80), nullable = True)
    bls_code_part = db.Column(db.String(1), nullable = True)


class FoodSubGroup(db.Model):
    __tablename__ = 'food_subgroup'
    id = db.Column(db.Integer, primary_key = True)
    titleEN = db.Column(db.String(80), nullable = False)
    titleDE = db.Column(db.String(80), nullable = True)
    food_maingroup_id = db.Column(db.Integer, db.ForeignKey('food_maingroup.id'), nullable = False)
    bls_code_part = db.Column(db.String(2), nullable = True)


class Material(db.Model):
    __tablename__ = 'materials'
    id = db.Column(db.Integer, primary_key = True)
    private = db.Column(db.Boolean, unique = False, default = False)  # user specific food that is not refered to a NDB or similar
    user_group_id = db.Column(db.Integer,db.ForeignKey('user_groups.id'), nullable = True)  # only required for private food items, for example home made foods
    titleEN = db.Column(db.String(160), nullable = True)
    titleDE = db.Column(db.String(160), nullable = True)
    bls_code = db.Column(db.String(7), nullable = True)
    ndb_code = db.Column(db.String(7), nullable = True)
    isBaseFood = db.Column(db.Boolean, unique = False, default = False)
    parentBaseFood = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable = True)
    # Standard values
    uom_nutrient_value = db.Column(db.String(5), db.ForeignKey('units_of_measures.uom'), nullable = True)
    # Classification
    food_maingroup_id = db.Column(db.Integer, db.ForeignKey('food_maingroup.id'), nullable = True)
    food_subgroup_id = db.Column(db.Integer, db.ForeignKey('food_subgroup.id'), nullable = True)
    food_processing_type_id = db.Column(db.Integer, db.ForeignKey('food_processing_type.id'), nullable = True)
    food_preparation_type_id = db.Column(db.Integer, db.ForeignKey('food_preparation_type.id'), nullable = True)
    food_edible_weight_id = db.Column(db.Integer, db.ForeignKey('food_weight_reference.id'), nullable = True)

    user_group = db.relationship("UserGroup")
    food_main_group = db.relationship("FoodMainGroup")
    food_subgroup = db.relationship("FoodSubGroup")
    food_processing_type = db.relationship("FoodProcessingType")
    food_preparation_type = db.relationship("FoodPreparationType")
    referencedIn = db.relationship("Ingredient")
    referencedInventoryItem = db.relationship("InventoryItem", back_populates="material")
    referencedMaterialForecast = db.relationship("MaterialForecast", back_populates="material")


# Forecast material consumption for a given inventory (e.g. household, warehouse)
# TODO: Consider link to InventoryItem (SKU) directly rather than to inventory and material_id
class MaterialForecast(db.Model):
    __tablename__ = 'material_forecasts'
    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventories.id'))
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=True, index=True)
    plan_date = db.Column(db.DateTime, nullable=True)
    quantity = db.Column(db.Float, nullable=True)
    quantity_uom = db.Column(db.String(5), db.ForeignKey('units_of_measures.uom'), nullable=True)

    inventory = db.relationship("Inventory", foreign_keys=[inventory_id], back_populates="material_forecasts")
    material = db.relationship("Material")
    uom = db.relationship("UOM")


class Inventory(db.Model):
    __tablename__ = 'inventories'
    id = db.Column(db.Integer, primary_key = True)
    creator_id = db.Column(db.Integer,db.ForeignKey('users.id'), nullable = False)
    user_group_id = db.Column(db.Integer,db.ForeignKey('user_groups.id'), nullable = True)

    creator = db.relationship("User", primaryjoin='User.id == Inventory.creator_id')
    user_group = db.relationship("UserGroup", foreign_keys=[user_group_id])
    items = db.relationship("InventoryItem", back_populates="inventory", cascade="all, delete-orphan")
    material_forecasts = db.relationship("MaterialForecast", back_populates="inventory", cascade="all, delete-orphan")


class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'
    id = db.Column(db.Integer, primary_key = True)  # TODO: Each item is per definition a SKU (Stock keeping unit), consider renaming
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventories.id'))
    titleEN = db.Column(db.String(160), nullable = True)  # TODO: remove those fields later and replace with good/food_id
    titleDE = db.Column(db.String(160), nullable = True)
    status = db.Column(db.SmallInteger, nullable = True)  # 0: No Need, 1 no stock, 2: insufficient stock, 3: sufficient stock
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable = True, index = True)
    level = db.Column(db.Integer, nullable = True)  # TODO: should be renamed to stock (on hand)
    need_from_diet_plan = db.Column(db.Integer, nullable = True)  # TODO: enhance? flat need from dietplans does not provide visibility and time clarity to dp elements
    need_additional = db.Column(db.Integer, nullable = True)
    re_order_level = db.Column(db.Integer, nullable = True)
    re_order_quantity = db.Column(db.Integer, nullable = True)

    inventory = db.relationship("Inventory", foreign_keys=[inventory_id], back_populates="items")
    material = db.relationship("Material")

    @property
    def serialize(self):
        #Returns object data in easily serializable format
        return {
            'id' : self.id,
            'inventory_id' : self.inventory_id,
            'titleEN' : self.titleEN,
            'titleDE' : self.titleDE,
            'status' : self.status,
            'material_id' : self.material_id,
            'level' : self.level,
            'need_from_diet_plan' : self.need_from_diet_plan,
            'need_additional' : self.need_additional,
            're_order_level' : self.re_order_level,
            're_order_quantity' : self.re_order_quantity
        }

# The shopping list or order with access to a group
class ShoppingOrder(db.Model):
    __tablename__ = 'shopping_orders'
    id = db.Column(db.Integer, primary_key = True)
    status = db.Column(db.SmallInteger, nullable = True)  # 0: closed, 1: open
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    closed = db.Column(db.DateTime, nullable = True)
    creator_id = db.Column(db.Integer,db.ForeignKey('users.id'), nullable = False)
    user_group_id = db.Column(db.Integer,db.ForeignKey('user_groups.id'), nullable = True)

    creator = db.relationship("User")
    user_group = db.relationship("UserGroup")
    items = db.relationship("ShoppingOrderItem", cascade="all, delete-orphan")


# Items on a shopping list that must be bought / ordered
class ShoppingOrderItem(db.Model):
    __tablename__ = 'shopping_order_items'
    id = db.Column(db.Integer, primary_key = True)
    titleEN = db.Column(db.String(80), nullable = True)  # TODO: remove those fields later and replace with good/food_id
    titleDE = db.Column(db.String(80), nullable = True)
    shopping_order_id = db.Column(db.Integer, db.ForeignKey('shopping_orders.id'))
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable = True)
    quantity = db.Column(db.Float, nullable = True)
    quantity_uom = db.Column(db.String(5), db.ForeignKey('units_of_measures.uom'), nullable = True)
    in_basket = db.Column(db.Boolean, default = False)
    in_basket_time = db.Column(db.DateTime, nullable = True)
    in_basket_geo_lon = db.Column(db.Float, nullable = True)
    in_basket_geo_lat = db.Column(db.Float, nullable = True)
    sort_order = db.Column(db.SmallInteger, nullable = True)
    item_photo = db.Column(db.String, nullable = True)
    barcode_photo = db.Column(db.String, nullable = True)
    ingredients_photo = db.Column(db.String, nullable = True)
    trade_item_id = db.Column(db.Integer, db.ForeignKey('trade_items.id'), nullable = True)

    material = db.relationship("Material")
    shopping_order = db.relationship("ShoppingOrder")
    trade_item = db.relationship("TradeItem")


class PlaningPeriodTemplate(db.Model):
    __tablename__ = 'planing_period_templates'
    id = db.Column(db.Integer, primary_key = True)
    start_date = db.Column(db.Date, nullable = True)
    end_date = db.Column(db.Date, nullable = True)
    week_no = db.Column(db.SmallInteger, nullable = True)


class DietPlan(db.Model):
    __tablename__ = 'diet_plans'
    id = db.Column(db.Integer, primary_key = True)
    creator_id = db.Column(db.Integer,db.ForeignKey('users.id'), nullable = False)
    user_group_id = db.Column(db.Integer,db.ForeignKey('user_groups.id'), nullable = True)

    items = db.relationship("DietPlanItem", cascade="all, delete-orphan")
    creator = db.relationship("User", primaryjoin='User.id == DietPlan.creator_id')
    user_group = db.relationship("UserGroup")


class DietPlanItem(db.Model):
    __tablename__ = 'diet_plan_items'
    id = db.Column(db.Integer, primary_key = True)
    diet_plan_id = db.Column(db.Integer, db.ForeignKey('diet_plans.id'), nullable=False)
    meal_id = db.Column(db.Integer, db.ForeignKey('meals.id'), nullable=False)
    plan_date = db.Column(db.Date, nullable=False)
    portions = db.Column(db.SmallInteger, nullable=True)
    consumed = db.Column(db.Boolean, nullable=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable = True)  # TODO: Allow individual food items to be placed in a dietplan, like an apple a day keeps the doctor away

    dietplan = db.relationship("DietPlan")
    meal = db.relationship("Meal", back_populates="diet_plans")

    @property
    def serialize(self):
        #Returns object data in easily serializable format
        return {
            'id' : self.id,
            'diet_plan_id' : self.diet_plan_id,
            'plan_date' : self.plan_date,
            'meal_id' : self.meal_id,
            'material_id' : self.material_id,
            'meal' : self.meal.title,
            'portions' : self.portions,
            'consumed' : self.consumed,
        }


# Items that relate to real products bought in the retail / grocery stores
class TradeItem(db.Model):
    __tablename__ = 'trade_items'
    id = db.Column(db.Integer, primary_key = True)
    ean = db.Column(db.String(13), nullable = True)
    upc = db.Column(db.String(13), nullable = True)
    gtin = db.Column(db.String(14), nullable = True)
    titleEN = db.Column(db.String(80), nullable = False)
    titleDE = db.Column(db.String(80), nullable = True)


class Place(db.Model):
    __tablename__ = 'places'
    id = db.Column(db.Integer, primary_key = True)
    titleEN = db.Column(db.String(80), nullable = False)  # storing google data not allowed except place id
    titleDE = db.Column(db.String(80), nullable = True)
    google_place_id = db.Column(db.String(80), nullable = True)
    geo_lat = db.Column(db.Float, nullable = True)
    geo_lng = db.Column(db.Float, nullable = True)

    @property
    def serialize(self):
        #Returns object data in easily serializable format
        return {
            'id' : self.id,
            'titleEN' : self.titleEN,
            'titleDE' : self.titleDE,
            'google_place_id' : self.google_place_id,
            'geo_lat' : self.geo_lat,
            'geo_lng' : self.geo_lng
        }

class FoodProcessingType(db.Model):
    __tablename__ = 'food_processing_type'
    id = db.Column(db.Integer, primary_key = True)
    bls_code_part = db.Column(db.String(1), nullable = True)
    food_subgroup_id = db.Column(db.Integer, db.ForeignKey('food_subgroup.id'), nullable = True) # Some foods to have specific processing types
    titleEN = db.Column(db.String(80), nullable = False)
    titleDE = db.Column(db.String(80), nullable = False)


class FoodPreparationType(db.Model):
    __tablename__ = 'food_preparation_type'
    id = db.Column(db.Integer, primary_key = True)
    bls_code_part = db.Column(db.String(1), nullable = True)
    food_maingroup_id = db.Column(db.Integer, db.ForeignKey('food_maingroup.id'), nullable = True)
    titleEN = db.Column(db.String(80), nullable = False)
    titleDE = db.Column(db.String(80), nullable = False)


class FoodEdibleWeight(db.Model):
    __tablename__ = 'food_weight_reference'
    id = db.Column(db.Integer, primary_key = True)
    bls_code_part = db.Column(db.String(1), nullable = True)


# ++++++++++++++++++++++++

class FoodComposition(db.Model):
    __tablename__ = 'food_composition'
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), primary_key = True)
    nutrient_id = db.Column(db.Integer, db.ForeignKey('nutrients.id'), primary_key = True)
    per_qty_uom = db.Column(db.String(length=5, convert_unicode=True), db.ForeignKey('units_of_measures.uom')) # example per grams of quantity
    per_qty = db.Column(db.Float)  # example per 100 of uom (grams)
    value = db.Column(db.Float)

    uom = db.relationship("UOM")


class Nutrient(db.Model):
    __tablename__ = 'nutrients'
    id = db.Column(db.Integer, primary_key = True)
    value_uom = db.Column(db.String(5), db.ForeignKey('units_of_measures.uom'))  # example calories, or milligrams
    titleEN = db.Column(db.String(80), nullable = False)
    titleDE = db.Column(db.String(80), nullable = True)

    uom = db.relationship("UOM")
