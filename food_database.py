# This module uses Object Relational Mapping via sqlalchemy
# in order to declare the mapping between object classes and
# database tables. The script creates those database tables.

import datetime

from sqlalchemy import create_engine
from sqlalchemy import (Column,
                        ForeignKey,
                        Integer,
                        SmallInteger,
                        String,
                        DateTime,
                        Date,
                        Float,
                        Boolean)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
# password encryption into hash
from passlib.apps import custom_app_context as pwd_context

# libraries for token generation
import random
import string
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature,
                          SignatureExpired)

# secret key required for encrypting a token
secret_key = ''.join(
    random.choice(
        string.ascii_uppercase + string.digits) for x in range(32))

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False, unique=True)
    picture = Column(String(250), nullable=True)
    provider = Column(String(250), nullable=True)
    provider_id = Column(String(250), nullable=True)
    active = Column(Boolean(), default=True)
    confirmed_at = Column(DateTime())
    password_hash = Column(String(255))
    language = Column(String(6), nullable=False)
    default_diet_plan_id = Column(Integer, ForeignKey('diet_plans.id'), nullable=True)
    default_inventory_id = Column(Integer, ForeignKey('inventories.id'), nullable=True)

    groups = relationship("UserGroupAssociation", back_populates="user")
    meals = relationship("Meal", cascade="all, delete-orphan")
    inventories = relationship("Inventory", primaryjoin='User.id == Inventory.creator_id', cascade="all, delete-orphan")
    diet_plans = relationship("DietPlan", primaryjoin='User.id == DietPlan.creator_id', cascade="all, delete-orphan", back_populates="creator")
    shopping_order = relationship("ShoppingOrder", cascade="all, delete-orphan")

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration):
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})

    # TODO: Understand properties based on Flask-login
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


class UserGroupAssociation(Base):
    __tablename__ = 'user_group_association'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    user_group_id = Column(Integer, ForeignKey('user_groups.id'), primary_key=True)
    is_owner = Column(Boolean, unique = False, default = False)

    group = relationship("UserGroup", back_populates="users")
    user = relationship("User", back_populates="groups")

# Required to provide access for the whole family on shopping lists
# Every user gets their own group unless their are added to another Group
# For now a user can only be in one group/family
class UserGroup(Base):
    __tablename__ = 'user_groups'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    # owner_id = Column(Integer, ForeignKey('users.id'))
    # owner_id = Column(Integer, nullable=False)
    # fk_owner = ForeignKeyConstraint(['users.id'], ['owner_id'])
    picture = Column(String(250), nullable=True)

    users = relationship("UserGroupAssociation", back_populates="group")

    # owner = relationship("User", foreign_keys=[owner_id], post_update=True)


class UOM(Base):
    __tablename__ = 'units_of_measures'
    uom = Column(String(length=5, convert_unicode=True), primary_key = True)
    longEN = Column(String(80), nullable = True)
    shortDE = Column(String(5), nullable = True)
    longDE = Column(String(80), nullable = True)
    type = Column(String(1), nullable = True) # 1 = ingredients only, 2 = both, 3 = nutrients only


class Meal(Base):
    __tablename__ = 'meals'
    id = Column(Integer, primary_key = True)
    title = Column(String(80), nullable = False)
    description = Column(String(250), nullable = True)
    portions = Column(SmallInteger, nullable = True)
    calories = Column(String(20), nullable = True)
    rating = Column(SmallInteger, nullable = True)
    image = Column(String, nullable = True)
    created = Column(DateTime, default = datetime.datetime.utcnow)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable = False)
    user_group_id = Column(Integer, ForeignKey('user_groups.id'))

    owner = relationship("User", back_populates="meals", foreign_keys=[owner_id])
    user_group = relationship("UserGroup")
    ingredients = relationship("Ingredient", cascade="all, delete-orphan")
    diet_plans = relationship("DietPlanItem", back_populates="meal", cascade="all, delete-orphan")

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

class Ingredient(Base):
    __tablename__ = 'ingredients'
    id = Column(Integer, primary_key = True)
    quantity = Column(Float, nullable = False)
    uom_id = Column(String(5), ForeignKey('units_of_measures.uom'), nullable = False)
    meal_id = Column(Integer, ForeignKey('meals.id'), nullable = False)
    title = Column(String(80), nullable = False) #gehackte Dosentomaten
    titleEN = Column(String(80), nullable = True) #chopped canned tomatoes
    processing_part = Column(String(80), nullable = True) # chopped canned
    preparation_part = Column(String(80), nullable = True) # empty
    base_food_part = Column(String(80), nullable = True) # Tomatoe

    food_id = Column(Integer, ForeignKey('foods.id'), nullable = True)
    created = Column(DateTime, default = datetime.datetime.utcnow)

    food = relationship("Food")
    meal = relationship("Meal", back_populates="ingredients")
    uom = relationship("UOM")


# based on german classification system BLS (Bundeslebensmittelschlüssel)
# consider integrating directly using a server license https://www.blsdb.de/license


class FoodMainGroup(Base):
    __tablename__ = 'food_maingroup'
    id = Column(Integer, primary_key = True)
    titleEN = Column(String(80), nullable = False)
    titleDE = Column(String(80), nullable = True)
    bls_code_part = Column(String(1), nullable = True)

class FoodSubGroup(Base):
    __tablename__ = 'food_subgroup'
    id = Column(Integer, primary_key = True)
    titleEN = Column(String(80), nullable = False)
    titleDE = Column(String(80), nullable = True)
    food_maingroup_id = Column(Integer, ForeignKey('food_maingroup.id'), nullable = False)
    bls_code_part = Column(String(2), nullable = True)

class Food(Base):
    __tablename__ = 'foods'
    id = Column(Integer, primary_key = True)
    private = Column(Boolean, unique = False, default = False)  # user specific food that is not refered to a NDB or similar
    user_group_id = Column(Integer,ForeignKey('user_groups.id'), nullable = True)  # only required for private food items, for example home made foods
    titleEN = Column(String(160), nullable = True)
    titleDE = Column(String(160), nullable = True)
    bls_code = Column(String(7), nullable = True)
    ndb_code = Column(String(7), nullable = True)
    isBaseFood = Column(Boolean, unique = False, default = False)
    parentBaseFood = Column(Integer, ForeignKey('foods.id'), nullable = True)
    # Standard values
    uom_nutrient_value = Column(String(5), ForeignKey('units_of_measures.uom'), nullable = True)
    # Classification
    food_maingroup_id = Column(Integer, ForeignKey('food_maingroup.id'), nullable = True)
    food_subgroup_id = Column(Integer, ForeignKey('food_subgroup.id'), nullable = True)
    food_processing_type_id = Column(Integer, ForeignKey('food_processing_type.id'), nullable = True)
    food_preparation_type_id = Column(Integer, ForeignKey('food_preparation_type.id'), nullable = True)
    food_edible_weight_id = Column(Integer, ForeignKey('food_weight_reference.id'), nullable = True)

    user_group = relationship("UserGroup")
    food_main_group = relationship("FoodMainGroup")
    food_subgroup = relationship("FoodSubGroup")
    food_processing_type = relationship("FoodProcessingType")
    food_preparation_type = relationship("FoodPreparationType")
    referencedIn = relationship("Ingredient")


class Goods(Base):
    __tablename__ = 'goods'
    id = Column(Integer, primary_key = True)
    private = Column(Boolean, unique = False, default = False)  # user specific food that is not refered to a NDB or similar
    user_group_id = Column(Integer,ForeignKey('user_groups.id'), nullable = True)
    titleEN = Column(String(160), nullable = True)
    titleDE = Column(String(160), nullable = True)

    user_group = relationship("UserGroup")


class FoodProcessingType(Base):
    __tablename__ = 'food_processing_type'
    id = Column(Integer, primary_key = True)
    bls_code_part = Column(String(1), nullable = True)
    food_subgroup_id = Column(Integer, ForeignKey('food_subgroup.id'), nullable = True) # Some foods to have specific processing types
    titleEN = Column(String(80), nullable = False)
    titleDE = Column(String(80), nullable = False)


class FoodPreparationType(Base):
    __tablename__ = 'food_preparation_type'
    id = Column(Integer, primary_key = True)
    bls_code_part = Column(String(1), nullable = True)
    food_maingroup_id = Column(Integer, ForeignKey('food_maingroup.id'), nullable = True)
    titleEN = Column(String(80), nullable = False)
    titleDE = Column(String(80), nullable = False)


class FoodEdibleWeight(Base):
    __tablename__ = 'food_weight_reference'
    id = Column(Integer, primary_key = True)
    bls_code_part = Column(String(1), nullable = True)


# ++++++++++++++++++++++++

class FoodComposition(Base):
    __tablename__ = 'food_composition'
    food_id = Column(Integer, ForeignKey('foods.id'), primary_key = True)
    nutrient_id = Column(Integer, ForeignKey('nutrients.id'), primary_key = True)
    per_qty_uom = Column(String(length=5, convert_unicode=True), ForeignKey('units_of_measures.uom')) # example per grams of quantity
    per_qty = Column(Float)  # example per 100 of uom (grams)
    value = Column(Float)

    uom = relationship("UOM")


class Nutrient(Base):
    __tablename__ = 'nutrients'
    id = Column(Integer, primary_key = True)
    value_uom = Column(String(5), ForeignKey('units_of_measures.uom'))  # example calories, or milligrams
    titleEN = Column(String(80), nullable = False)
    titleDE = Column(String(80), nullable = True)

    uom = relationship("UOM")


class Inventory(Base):
    __tablename__ = 'inventories'
    id = Column(Integer, primary_key = True)
    creator_id = Column(Integer,ForeignKey('users.id'), nullable = False)
    user_group_id = Column(Integer,ForeignKey('user_groups.id'), nullable = True)

    creator = relationship("User", primaryjoin='User.id == Inventory.creator_id')
    user_group = relationship("UserGroup", foreign_keys=[user_group_id])
    items = relationship("InventoryItem", back_populates="inventory", cascade="all, delete-orphan")

class InventoryItem(Base):
    __tablename__ = 'inventory_items'
    id = Column(Integer, primary_key = True)
    inventory_id = Column(Integer, ForeignKey('inventories.id'))
    titleEN = Column(String(80), nullable = True)  # TODO: remove those fields later and replace with good/food_id
    titleDE = Column(String(80), nullable = True)
    status = Column(SmallInteger, nullable = True)  # 0: No Need, 1 no stock, 2: insufficient stock, 3: sufficient stock
    food_id = Column(Integer, ForeignKey('foods.id'), nullable = True)
    good_id = Column(Integer, ForeignKey('goods.id'), nullable = True)
    level = Column(Integer, nullable = True)
    need_from_diet_plan = Column(Integer, nullable = True)  # TODO: enhance? flat need from dietplans does not provide visibility and time clarity to dp elements
    need_additional = Column(Integer, nullable = True)
    re_order_level = Column(Integer, nullable = True)
    re_order_quantity = Column(Integer, nullable = True)

    inventory = relationship("Inventory", foreign_keys=[inventory_id], back_populates="items")
    food = relationship("Food")
    good = relationship("Goods")

    @property
    def serialize(self):
        #Returns object data in easily serializable format
        return {
            'id' : self.id,
            'inventory_id' : self.inventory_id,
            'titleEN' : self.titleEN,
            'titleDE' : self.titleDE,
            'status' : self.status,
            'food_id' : self.food_id,
            'good_id' : self.good_id,
            'level' : self.level,
            'need_from_diet_plan' : self.need_from_diet_plan,
            'need_additional' : self.need_additional,
            're_order_level' : self.re_order_level,
            're_order_quantity' : self.re_order_quantity
        }

# The shopping list or order with access to a group
class ShoppingOrder(Base):
    __tablename__ = 'shopping_orders'
    id = Column(Integer, primary_key = True)
    status = Column(SmallInteger, nullable = True)  # 0: closed, 1: open
    created = Column(DateTime, default = datetime.datetime.utcnow)
    closed = Column(DateTime, nullable = True)
    creator_id = Column(Integer,ForeignKey('users.id'), nullable = False)
    user_group_id = Column(Integer,ForeignKey('user_groups.id'), nullable = True)

    creator = relationship("User")
    user_group = relationship("UserGroup")
    items = relationship("ShoppingOrderItem", cascade="all, delete-orphan")


# Items on a shopping list that must be bought / ordered
class ShoppingOrderItem(Base):
    __tablename__ = 'shopping_order_items'
    id = Column(Integer, primary_key = True)
    titleEN = Column(String(80), nullable = True)  # TODO: remove those fields later and replace with good/food_id
    titleDE = Column(String(80), nullable = True)
    shopping_order_id = Column(Integer, ForeignKey('shopping_orders.id'))
    food_id = Column(Integer, ForeignKey('foods.id'), nullable = True)
    good_id = Column(Integer, ForeignKey('goods.id'), nullable = True)
    quantity = Column(Float, nullable = True)
    quantity_uom = Column(String(5), ForeignKey('units_of_measures.uom'), nullable = True)
    in_basket = Column(Boolean, default = False)
    in_basket_time = Column(DateTime, nullable = True)
    in_basket_geo_lon = Column(Float, nullable = True)
    in_basket_geo_lat = Column(Float, nullable = True)
    sort_order = Column(SmallInteger, nullable = True)
    item_photo = Column(String, nullable = True)
    barcode_photo = Column(String, nullable = True)
    ingredients_photo = Column(String, nullable = True)
    trade_item_id = Column(Integer, ForeignKey('trade_items.id'), nullable = True)

    food = relationship("Food")
    good = relationship("Goods")
    shopping_order = relationship("ShoppingOrder")
    trade_item = relationship("TradeItem")


class PlaningPeriodTemplate(Base):
    __tablename__ = 'planing_period_templates'
    id = Column(Integer, primary_key = True)
    start_date = Column(Date, nullable = True)
    end_date = Column(Date, nullable = True)
    week_no = Column(SmallInteger, nullable = True)


class DietPlan(Base):
    __tablename__ = 'diet_plans'
    id = Column(Integer, primary_key = True)
    creator_id = Column(Integer,ForeignKey('users.id'), nullable = False)
    user_group_id = Column(Integer,ForeignKey('user_groups.id'), nullable = True)

    items = relationship("DietPlanItem", cascade="all, delete-orphan")
    creator = relationship("User", primaryjoin='User.id == DietPlan.creator_id')
    user_group = relationship("UserGroup")


class DietPlanItem(Base):
    __tablename__ = 'diet_plan_items'
    id = Column(Integer, primary_key = True)
    diet_plan_id = Column(Integer, ForeignKey('diet_plans.id'), nullable=False)
    meal_id = Column(Integer, ForeignKey('meals.id'), nullable=False)
    plan_date = Column(Date, nullable=False)
    portions = Column(SmallInteger, nullable=True)
    consumed = Column(Boolean, nullable=True)

    dietplan = relationship("DietPlan")
    meal = relationship("Meal", back_populates="diet_plans")

    @property
    def serialize(self):
        #Returns object data in easily serializable format
        return {
            'id' : self.id,
            'diet_plan_id' : self.diet_plan_id,
            'plan_date' : self.plan_date,
            'meal_id' : self.meal_id,
            'meal' : self.meal.title,
            'portions' : self.portions,
            'consumed' : self.consumed,
        }

# Items that relate to real products bought in the retail / grocery stores
class TradeItem(Base):
    __tablename__ = 'trade_items'
    id = Column(Integer, primary_key = True)
    ean = Column(String(13), nullable = True)
    upc = Column(String(13), nullable = True)
    gtin = Column(String(14), nullable = True)
    titleEN = Column(String(80), nullable = False)
    titleDE = Column(String(80), nullable = True)


class Place(Base):
    __tablename__ = 'places'
    id = Column(Integer, primary_key = True)
    titleEN = Column(String(80), nullable = False)  # storing google data not allowed except place id
    titleDE = Column(String(80), nullable = True)
    google_place_id = Column(String(80), nullable = True)
    geo_lat = Column(Float, nullable = True)
    geo_lng = Column(Float, nullable = True)

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

####### insert at end of file #######

#engine = create_engine('postgresql://vagrant:vagrant@127.0.0.1:5432/np')
engine = create_engine('postgres://njxqkgsvotldpo:0091ec1051866196d42e608aadc421ef9bb58c37d9fcfe0e7bac4e9ce63929f8@ec2-54-228-182-57.eu-west-1.compute.amazonaws.com:5432/ddjblvctcusagj')

# TODO: Ensure that drop cascade works or try to use SQLAlchemy-Migrate
# Do not enable this it will cause flask debugger to hang!
# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
