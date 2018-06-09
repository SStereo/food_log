from huntingfood import db
from huntingfood import ma
from marshmallow import fields

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
    default_consumption_plan_id = db.Column(db.Integer, db.ForeignKey('consumption_plans.id'), nullable=True, unique=True)
    default_portions = db.Column(db.SmallInteger, nullable=True)
    street = db.Column(db.String(120), nullable=True)
    city = db.Column(db.String(120), nullable=True)
    state = db.Column(db.String(120), nullable=True)
    zip = db.Column(db.String(120), nullable=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    groups = db.relationship("UserGroupAssociation", back_populates="user")
    meals = db.relationship("Meal", cascade="all, delete-orphan", back_populates="owner")
    inventories = db.relationship(
        "Inventory",
        primaryjoin='User.id == Inventory.creator_id',
        back_populates="creator",
        cascade="all, delete-orphan")
    diet_plans = db.relationship("DietPlan", primaryjoin='User.id == DietPlan.creator_id', cascade="all, delete-orphan", back_populates="creator")
    consumption_plans = db.relationship("ConsumptionPlan", primaryjoin='User.id == ConsumptionPlan.creator_id', cascade="all, delete-orphan", back_populates="creator")
    default_diet_plan = db.relationship("DietPlan", primaryjoin='User.default_diet_plan_id == DietPlan.id', cascade="all, delete-orphan", single_parent=True)
    default_inventory = db.relationship("Inventory", primaryjoin='User.default_inventory_id == Inventory.id', cascade="all, delete-orphan", single_parent=True)
    default_consumption_plan = db.relationship("ConsumptionPlan", primaryjoin='User.default_consumption_plan_id == ConsumptionPlan.id', cascade="all, delete-orphan", single_parent=True)
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

    @property
    def serialize(self):
        # Returns object data in easily serializable format
        return {
            'user_id': self.id,
            'name': self.name,
            'email': self.email,
            'picture': self.picture,
            'provider': self.provider,
            'active': self.active,
            'language': self.language,
            'default_diet_plan_id': self.default_diet_plan_id,
            'default_inventory_id': self.default_inventory_id,
            'default_portions': self.default_portions,
            'street': self.street,
            'city': self.city,
            'state': self.state,
            'zip': self.zip,
        }


class UserGroupAssociation(db.Model):
    __tablename__ = 'user_group_association'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    user_group_id = db.Column(db.Integer, db.ForeignKey('user_groups.id'), primary_key=True)
    is_owner = db.Column(db.Boolean, unique=False, default=False)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

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
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    users = db.relationship("UserGroupAssociation", back_populates="group")
    # owner = db.relationship("User", foreign_keys=[owner_id], post_update=True)


class UOM(db.Model):
    __tablename__ = 'units_of_measures'
    uom = db.Column(db.String(length=5, convert_unicode=True), primary_key=True)
    longEN = db.Column(db.String(80), nullable=True)
    shortDE = db.Column(db.String(5), nullable=True)
    longDE = db.Column(db.String(80), nullable=True)
    type = db.Column(db.String(1), nullable=True)  # 1 = ingredients only, 2 = both, 3 = nutrients only
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class Meal(db.Model):
    __tablename__ = 'meals'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(250), nullable=True)
    portions = db.Column(db.SmallInteger, nullable=True)
    calories = db.Column(db.String(20), nullable=True)
    rating = db.Column(db.SmallInteger, nullable=True)
    image = db.Column(db.String, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_group_id = db.Column(db.Integer, db.ForeignKey('user_groups.id'))
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    owner = db.relationship("User", back_populates="meals", foreign_keys=[owner_id])
    user_group = db.relationship("UserGroup")
    ingredients = db.relationship("Ingredient", back_populates="meal", cascade="all, delete-orphan")
    diet_plans = db.relationship("DietPlanItem", back_populates="meal", cascade="all, delete-orphan")

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'portions': self.portions,
            'rating': self.rating,
            'image': self.image,
            'created': self.created,
        }


class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Float, nullable=False)
    uom_id = db.Column(db.String(5), db.ForeignKey('units_of_measures.uom'), nullable=False)
    meal_id = db.Column(db.Integer, db.ForeignKey('meals.id'), nullable=False, index = True)
    title = db.Column(db.String(80), nullable=False)  # gehackte Dosentomaten
    titleEN = db.Column(db.String(80), nullable=True)  # TODO: obsolete
    processing_part = db.Column(db.String(80), nullable=True)  # chopped canned
    preparation_part = db.Column(db.String(80), nullable=True)  # empty
    base_food_part = db.Column(db.String(80), nullable=True)  # Tomatoe
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=True, index = True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    material = db.relationship("Material")
    meal = db.relationship("Meal", back_populates="ingredients")
    uom = db.relationship("UOM")


# based on german classification system BLS (Bundeslebensmittelschlüssel)
# consider integrating directly using a server license https://www.blsdb.de/license
class FoodMainGroup(db.Model):
    __tablename__ = 'food_maingroup'
    id = db.Column(db.Integer, primary_key=True)
    titleEN = db.Column(db.String(80), nullable=False)
    titleDE = db.Column(db.String(80), nullable=True)
    bls_code_part = db.Column(db.String(1), nullable=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class FoodSubGroup(db.Model):
    __tablename__ = 'food_subgroup'
    id = db.Column(db.Integer, primary_key=True)
    titleEN = db.Column(db.String(80), nullable=False)
    titleDE = db.Column(db.String(80), nullable=True)
    food_maingroup_id = db.Column(db.Integer, db.ForeignKey('food_maingroup.id'), nullable=False)
    bls_code_part = db.Column(db.String(2), nullable=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class Material(db.Model):
    __tablename__ = 'materials'
    id = db.Column(db.Integer, primary_key=True)
    private = db.Column(db.Boolean, unique = False, default = False)  # user specific food that is not refered to a NDB or similar
    user_group_id = db.Column(db.Integer, db.ForeignKey('user_groups.id'), nullable=True)  # only required for private food items, for example home made foods
    title = db.Column(db.String(160), nullable=True)
    language_code = db.Column(db.String(8), nullable=False)
    titleEN = db.Column(db.String(160), nullable=True)
    standard_uom_id = db.Column(db.String(5), db.ForeignKey('units_of_measures.uom'), nullable=True)
    uom_base_id = db.Column(db.String(5), db.ForeignKey('units_of_measures.uom'), nullable=False)  # Physical, e.g. g (Sugar)
    uom_stock_id = db.Column(db.String(5), db.ForeignKey('units_of_measures.uom'), nullable=True)  # One updated on an inventory, updated here for future inventories
    uom_issue_id = db.Column(db.String(5), db.ForeignKey('units_of_measures.uom'), nullable=True)  # tbsp (4 table spoons of sugar)
    bls_code = db.Column(db.String(7), nullable=True)
    ndb_code = db.Column(db.String(7), nullable=True)
    ndb_title = db.Column(db.String(160), nullable=True)
    isBaseFood = db.Column(db.Boolean, unique = False, default = False)
    parentBaseFood = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # Standard values
    uom_nutrient_value = db.Column(db.String(5), db.ForeignKey('units_of_measures.uom'), nullable=True)
    # Classification
    food_maingroup_id = db.Column(db.Integer, db.ForeignKey('food_maingroup.id'), nullable=True)
    food_subgroup_id = db.Column(db.Integer, db.ForeignKey('food_subgroup.id'), nullable=True)
    food_processing_type_id = db.Column(db.Integer, db.ForeignKey('food_processing_type.id'), nullable=True)
    food_preparation_type_id = db.Column(db.Integer, db.ForeignKey('food_preparation_type.id'), nullable=True)
    food_edible_weight_id = db.Column(db.Integer, db.ForeignKey('food_weight_reference.id'), nullable=True)

    user_group = db.relationship("UserGroup")
    food_main_group = db.relationship("FoodMainGroup")
    food_subgroup = db.relationship("FoodSubGroup")
    food_processing_type = db.relationship("FoodProcessingType")
    food_preparation_type = db.relationship("FoodPreparationType")
    referencedIn = db.relationship("Ingredient")
    referencedInventoryItem = db.relationship("InventoryItem", back_populates="material")
    referencedMaterialForecast = db.relationship("MaterialForecast", back_populates="material")
    standard_uom = db.relationship("UOM", foreign_keys=[standard_uom_id])
    base_uom = db.relationship("UOM", foreign_keys=[uom_base_id])
    stock_uom = db.relationship("UOM", foreign_keys=[uom_stock_id])
    issue_uom = db.relationship("UOM", foreign_keys=[uom_issue_id])


# Converts issue units like table spoons ore cups into base units like grams
class MaterialUnits:
    __tablename__ = 'material_units'
    id = db.Column(
        db.Integer,
        primary_key=True)
    material_id = db.Column(
        db.Integer,
        db.ForeignKey('materials.id'),
        nullable=True, index=True)
    uom_id = db.Column(
        db.String(5),
        db.ForeignKey('units_of_measures.uom'),
        nullable=False)
    uom_factor_to_base = db.Column(
        db.Float,
        nullable=True)  # e.g. 1 tbsp (issue) = 20 g (base)


# Forecast material consumption for a given inventory (e.g. house, warehouse)
# TODO: Consider link to InventoryItem (SKU)
class MaterialForecast(db.Model):
    __tablename__ = 'material_forecasts'
    id = db.Column(
        db.Integer,
        primary_key=True)
    inventory_id = db.Column(
        db.Integer,
        db.ForeignKey('inventories.id'))
    material_id = db.Column(
        db.Integer,
        db.ForeignKey('materials.id'),
        nullable=True, index=True)
    type = db.Column(
        db.SmallInteger,
        nullable=False)
    # 0 = planned demand (dietplan)
    # 1 = periodic consumption
    # 2 = other demand
    plan_date_start = db.Column(
        db.DateTime(timezone=True),
        nullable=True)
    plan_date_end = db.Column(
        db.DateTime(timezone=True),
        nullable=True)
    quantity = db.Column(
        db.Float,
        nullable=True)
    quantity_per_day = db.Column(
        db.Float,
        nullable=True)
    quantity_uom = db.Column(
        db.String(5),
        db.ForeignKey('units_of_measures.uom'),
        nullable=True)
    consumption_plan_item_id = db.Column(
        db.Integer,
        db.ForeignKey('consumption_plan_items.id'),
        nullable=True)
    diet_plan_item_id = db.Column(
        db.Integer,
        db.ForeignKey('diet_plan_items.id'),
        nullable=True)
    created = db.Column(
        db.DateTime,
        default=datetime.datetime.utcnow)

    inventory = db.relationship(
        "Inventory",
        foreign_keys=[inventory_id],
        back_populates="material_forecasts")
    material = db.relationship(
        "Material")
    uom = db.relationship(
        "UOM")
    consumption_plan_item = db.relationship(
        "ConsumptionPlanItem")

    inventory_item = db.relationship(
        "InventoryItem",
        foreign_keys=[inventory_id, material_id],
        primaryjoin="and_(MaterialForecast.inventory_id==InventoryItem.inventory_id, MaterialForecast.material_id==InventoryItem.material_id)",
        backref='forecasts')

    @property
    def serialize(self):
        return {
            'id': self.id,
            'inventory_id': self.inventory_id,
            'material_id': self.material_id,
            'plan_date': self.plan_date,
            'plan_date_start': self.plan_date_start,
            'plan_date_end': self.plan_date_end,
            'quantity': self.quantity,
            'quantity_uom': self.quantity_uom
        }


# The location from where the materials are taken for consumption
# Examples: home, holiday home, boat
# TODO: Link to a location table
class Inventory(db.Model):
    __tablename__ = 'inventories'
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_group_id = db.Column(db.Integer, db.ForeignKey('user_groups.id'), nullable=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    creator = db.relationship(
        "User",
        back_populates="inventories",
        primaryjoin='User.id == Inventory.creator_id')
    material_forecasts = db.relationship("MaterialForecast", back_populates="inventory", cascade="all, delete-orphan")
    user_group = db.relationship("UserGroup", foreign_keys=[user_group_id])
    items = db.relationship("InventoryItem", back_populates="inventory", cascade="all, delete-orphan")


class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'
    id = db.Column(db.Integer, primary_key=True)  # TODO: Each item is per definition a SKU (Stock keeping unit), consider renaming
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventories.id'))
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=True, index=True)
    titleEN = db.Column(db.String(160), nullable=True)
    title = db.Column(db.String(160), nullable=True)
    uom_stock_id = db.Column(db.String(5), db.ForeignKey('units_of_measures.uom'), nullable=True)
    uom_base_id = db.Column(db.String(5), db.ForeignKey('units_of_measures.uom'), nullable=False)
    quantity_stock = db.Column(db.Float, nullable=True)
    quantity_stock_user = db.Column(db.Float, nullable=True)
    quantity_base = db.Column(db.Float, nullable=True)
    quantity_base_user = db.Column(db.Float, nullable=True)  # save the quantity entered by the user to recover it from auto toggle setting
    quantity_conversion_factor = db.Column(db.Float, nullable=True)  # to calculate issue units from stock units
    level = db.Column(db.Float, nullable=True)  # TODO: should be renamed to stock (on hand)
    re_order_level = db.Column(db.Integer, nullable=True)
    re_order_quantity = db.Column(db.Integer, nullable=True)
    ignore_forecast = db.Column(db.Boolean, unique=False, default=False)  # Any forecast is ignored so the status will calculate to 0: No Need
    # type:
    # 0 = no regular consumption
    # 1 = every day
    # 2 = once a week
    # 3 = once a month
    # 4 = once a year
    cp_type = db.Column(db.SmallInteger, nullable=False, default=0)
    cp_quantity = db.Column(db.Float, nullable=True)
    cp_plan_date = db.Column(db.DateTime(timezone=True), nullable=True)  # TODO: obsolete
    cp_plan_date_start = db.Column(db.DateTime(timezone=True), nullable=True)
    cp_plan_date_end = db.Column(db.DateTime(timezone=True), nullable=True)
    cp_period = db.Column(db.SmallInteger, nullable=True)
    # 0 = daily
    # 1 = weekly
    # 2 = monthly
    # 3 = yearly
    cp_weekday = db.Column(db.SmallInteger, nullable=True)
    cp_day_in_month = db.Column(db.SmallInteger, nullable=True)
    cp_end_date = db.Column(db.DateTime(timezone=True), nullable=True)  # TODO: depreciated

    op_plan_date_start = db.Column(db.DateTime(timezone=True), nullable=True)
    op_plan_date_end = db.Column(db.DateTime(timezone=True), nullable=True)
    op_quantity = db.Column(db.Float, nullable=True)

    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    inventory = db.relationship("Inventory", foreign_keys=[inventory_id], back_populates="items")
    material = db.relationship("Material")
    uom_base = db.relationship("UOM", foreign_keys=[uom_base_id])
    uom_stock = db.relationship("UOM", foreign_keys=[uom_stock_id])

    @property
    def serialize(self):
        return {
            'id': self.id,
            'inventory_id': self.inventory_id,
            'titleEN': self.titleEN,
            'title': self.title,
            'material_id': self.material_id,
            'level': self.level,
            'ignore_forecast': self.ignore_forecast,
            're_order_level': self.re_order_level,
            're_order_quantity': self.re_order_quantity
        }


# The shopping list or order with access to a group
class ShoppingOrder(db.Model):
    __tablename__ = 'shopping_orders'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.SmallInteger, nullable=True)  # 0: closed, 1: open
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    closed = db.Column(db.DateTime, nullable=True)
    creator_id = db.Column(db.Integer,db.ForeignKey('users.id'), nullable=False)
    user_group_id = db.Column(db.Integer,db.ForeignKey('user_groups.id'), nullable=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    creator = db.relationship("User")
    user_group = db.relationship("UserGroup")
    items = db.relationship("ShoppingOrderItem", cascade="all, delete-orphan")


# Items on a shopping list that must be bought / ordered
class ShoppingOrderItem(db.Model):
    __tablename__ = 'shopping_order_items'
    id = db.Column(db.Integer, primary_key=True)
    titleEN = db.Column(db.String(80), nullable=True)  # TODO: remove those fields later and replace with good/food_id
    titleDE = db.Column(db.String(80), nullable=True)
    title = db.Column(db.String(80), nullable=True)
    shopping_order_id = db.Column(db.Integer, db.ForeignKey('shopping_orders.id'))
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=True)
    quantity = db.Column(db.Float, nullable=True)
    quantity_uom = db.Column(db.String(5), db.ForeignKey('units_of_measures.uom'), nullable=True)
    in_basket = db.Column(db.Boolean, default = False)
    in_basket_time = db.Column(db.DateTime, nullable=True)
    in_basket_geo_lon = db.Column(db.Float, nullable=True)
    in_basket_geo_lat = db.Column(db.Float, nullable=True)
    sort_order = db.Column(db.SmallInteger, nullable=True)
    item_photo = db.Column(db.String, nullable=True)
    barcode_photo = db.Column(db.String, nullable=True)
    ingredients_photo = db.Column(db.String, nullable=True)
    trade_item_id = db.Column(db.Integer, db.ForeignKey('trade_items.id'), nullable=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    material = db.relationship("Material")
    shopping_order = db.relationship("ShoppingOrder")
    trade_item = db.relationship("TradeItem")


class DietPlan(db.Model):
    __tablename__ = 'diet_plans'
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer,db.ForeignKey('users.id'), nullable=False)
    user_group_id = db.Column(db.Integer,db.ForeignKey('user_groups.id'), nullable=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    items = db.relationship("DietPlanItem", cascade="all, delete-orphan")
    creator = db.relationship("User", primaryjoin='User.id == DietPlan.creator_id')
    user_group = db.relationship("UserGroup")


class DietPlanItem(db.Model):
    __tablename__ = 'diet_plan_items'
    id = db.Column(db.Integer, primary_key=True)
    diet_plan_id = db.Column(db.Integer, db.ForeignKey('diet_plans.id'), nullable=False)
    meal_id = db.Column(db.Integer, db.ForeignKey('meals.id'), nullable=False)
    plan_date = db.Column(db.DateTime(timezone=True), nullable=False)
    portions = db.Column(db.SmallInteger, nullable=True)
    consumed = db.Column(db.Boolean, nullable=True)
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=True)  # TODO: Allow individual food items to be placed in a dietplan, like an apple a day keeps the doctor away
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    dietplan = db.relationship("DietPlan")
    meal = db.relationship("Meal", back_populates="diet_plans")

    @property
    def serialize(self):
        return {
            'id': self.id,
            'diet_plan_id': self.diet_plan_id,
            'plan_date': self.plan_date,
            'meal_id': self.meal_id,
            'material_id': self.material_id,
            'meal': self.meal.title,
            'portions': self.portions,
            'consumed': self.consumed,
        }


class ConsumptionPlan(db.Model):
    __tablename__ = 'consumption_plans'
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_group_id = db.Column(db.Integer, db.ForeignKey('user_groups.id'), nullable=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    items = db.relationship("ConsumptionPlanItem", cascade="all, delete-orphan")
    creator = db.relationship("User", primaryjoin='User.id == ConsumptionPlan.creator_id')
    user_group = db.relationship("UserGroup")


class ConsumptionPlanItem(db.Model):
    __tablename__ = 'consumption_plan_items'
    id = db.Column(db.Integer, primary_key=True)
    consumption_plan_id = db.Column(db.Integer, db.ForeignKey('consumption_plans.id'), nullable=False)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventories.id'))  # TODO: Rethink if this is right
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=True)  # TODO: Allow individual food items to be placed in a dietplan, like an apple a day keeps the doctor away
    # type:
    # 0 = one time consumption
    # 1 = periodical consumption
    type = db.Column(db.SmallInteger, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    plan_date = db.Column(db.DateTime(timezone=True), nullable=True)
    period = db.Column(db.SmallInteger, nullable=True)
    # null = non periodic type = 1
    # 1 = daily
    # 2 = weekly
    # 3 = monthly
    # 4 = yearly
    weekday = db.Column(db.SmallInteger, nullable=True)
    day_in_month = db.Column(db.SmallInteger, nullable=True)
    end_date = db.Column(db.DateTime(timezone=True), nullable=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    consumption_plan = db.relationship("ConsumptionPlan")

    @property
    def serialize(self):
        return {
            'id': self.id,
            'consumption_plan_id': self.consumption_plan_id,
            'material_id': self.material_id,
            'type': self.type,
            'quantity': self.quantity,
            'plan_date': self.plan_date,
            'period': self.period,
            'weekday': self.weekday,
            'day_in_month': self.day_in_month,
            'end_date': self.end_date,
            'created': self.created
        }


# Items that relate to real products bought in the retail / grocery stores
class TradeItem(db.Model):
    __tablename__ = 'trade_items'
    id = db.Column(db.Integer, primary_key=True)
    ean = db.Column(db.String(13), nullable=True)
    upc = db.Column(db.String(13), nullable=True)
    gtin = db.Column(db.String(14), nullable=True)
    titleEN = db.Column(db.String(80), nullable=False)
    titleDE = db.Column(db.String(80), nullable=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class Place(db.Model):
    __tablename__ = 'places'
    id = db.Column(db.Integer, primary_key=True)
    titleEN = db.Column(db.String(80), nullable=False)  # storing google data not allowed except place id
    titleDE = db.Column(db.String(80), nullable=True)  # TODO: obsolete
    title = db.Column(db.String(80), nullable=True)
    google_place_id = db.Column(db.String(80), nullable=True)
    geo_lat = db.Column(db.Float, nullable=True)
    geo_lng = db.Column(db.Float, nullable=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    @property
    def serialize(self):
        #Returns object data in easily serializable format
        return {
            'id' : self.id,
            'titleEN' : self.titleEN,
            'title' : self.title,
            'google_place_id' : self.google_place_id,
            'geo_lat' : self.geo_lat,
            'geo_lng' : self.geo_lng
        }


class FoodProcessingType(db.Model):
    __tablename__ = 'food_processing_type'
    id = db.Column(db.Integer, primary_key=True)
    bls_code_part = db.Column(db.String(1), nullable=True)
    food_subgroup_id = db.Column(db.Integer, db.ForeignKey('food_subgroup.id'), nullable=True) # Some foods to have specific processing types
    titleEN = db.Column(db.String(80), nullable=False)
    titleDE = db.Column(db.String(80), nullable=False)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class FoodPreparationType(db.Model):
    __tablename__ = 'food_preparation_type'
    id = db.Column(db.Integer, primary_key=True)
    bls_code_part = db.Column(db.String(1), nullable=True)
    food_maingroup_id = db.Column(db.Integer, db.ForeignKey('food_maingroup.id'), nullable=True)
    titleEN = db.Column(db.String(80), nullable=False)
    titleDE = db.Column(db.String(80), nullable=False)


class FoodEdibleWeight(db.Model):
    __tablename__ = 'food_weight_reference'
    id = db.Column(db.Integer, primary_key=True)
    bls_code_part = db.Column(db.String(1), nullable=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)


# ++++++++++++++++++++++++
class FoodComposition(db.Model):
    __tablename__ = 'food_composition'
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), primary_key=True)
    nutrient_id = db.Column(db.Integer, db.ForeignKey('nutrients.id'), primary_key=True)
    per_qty_uom = db.Column(db.String(length=5, convert_unicode=True), db.ForeignKey('units_of_measures.uom')) # example per grams of quantity
    per_qty = db.Column(db.Float)  # example per 100 of uom (grams)
    value = db.Column(db.Float)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    uom = db.relationship("UOM")


class Nutrient(db.Model):
    __tablename__ = 'nutrients'
    id = db.Column(db.Integer, primary_key=True)
    value_uom = db.Column(db.String(5), db.ForeignKey('units_of_measures.uom'))  # example calories, or milligrams
    titleEN = db.Column(db.String(80), nullable=False)
    titleDE = db.Column(db.String(80), nullable=True)  # TODO: obsolete
    title = db.Column(db.String(80), nullable=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    uom = db.relationship("UOM")


class Country(db.Model):
    __tablename__ = 'countries'
    name = db.Column(db.String(60), primary_key=True)
    alpha2 = db.Column(db.String(2), nullable=False)
    alpha3 = db.Column(db.String(3), nullable=True)
    country_code = db.Column(db.String(3), nullable=True)
    region = db.Column(db.String(60), nullable=True)
    sub_region = db.Column(db.String(60), nullable=True)
    intermediate_region = db.Column(db.String(60), nullable=True)
    region_code = db.Column(db.String(3), nullable=True)
    sub_region_code = db.Column(db.String(3), nullable=True)
    intermediate_region_code = db.Column(db.String(3), nullable=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    states = db.relationship("State", cascade="all, delete-orphan")


class State(db.Model):
    __tablename__ = 'states'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=True)
    country_name = db.Column(db.String(60), db.ForeignKey('countries.name'), nullable=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Marshmallow Schema Definitions
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class UOMSchema(ma.ModelSchema):
    class Meta:
        model = UOM


class MaterialSchema(ma.ModelSchema):
    created = fields.DateTime(dump_only=True)

    class Meta:
        model = Material
        fields = (
            'id',
            'private',
            'titleEN',
            'title',
            'standard_uom_id')


class MaterialForecastSchema(ma.ModelSchema):
    class Meta:
        model = MaterialForecast


class InventoryItemSchema(ma.ModelSchema):
    class Meta:
        model = InventoryItem
    forecasts = fields.Nested(MaterialForecastSchema,
                              many=True,
                              only=[
                                'id',
                                'type',
                                'plan_date_start',
                                'plan_date_end',
                                'quantity_per_day',
                                'quantity',
                                'quantity_uom'])
