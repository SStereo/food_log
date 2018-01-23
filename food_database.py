# This module uses Object Relational Mapping via sqlalchemy
# in order to declare the mapping between object classes and
# database tables. The script creates those database tables.
import os
import sys
import datetime

from sqlalchemy import create_engine
from sqlalchemy import (Column,
                        ForeignKey,
                        Integer,
                        SmallInteger,
                        String,
                        DateTime,
                        LargeBinary,
                        Float,
                        Boolean,
                        ForeignKeyConstraint)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
# Required for user password
from passlib.apps import custom_app_context as pwd_context

# Declarative Mapping

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250), nullable=True)
    username = Column(String(32), index=True)
    password_hash = Column(String(64))
    #group_id = Column(Integer, ForeignKey('user_groups.id'), nullable=True)
    #fk_user_group = ForeignKeyConstraint(['user_groups.id'], ['group_id'])

    groups = relationship("UserGroupAssociation", back_populates="user")
    meals = relationship("Meal", cascade="save-update, merge, delete")

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


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
    ingredients = relationship("Ingredient", cascade="save-update, merge, delete")

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
    user_group_id = Column(Integer,ForeignKey('user_groups.id'), nullable = False)

    creator = relationship("User", foreign_keys=[creator_id])
    user_group = relationship("UserGroup", foreign_keys=[user_group_id])


class InventoryItem(Base):
    __tablename__ = 'inventory_items'
    id = Column(Integer, primary_key = True)
    inventory_id = Column(Integer, ForeignKey('inventories.id'))
    food_id = Column(Integer, ForeignKey('foods.id'), nullable = True)
    good_id = Column(Integer, ForeignKey('goods.id'), nullable = True)
    level = Column(Integer, nullable = True)
    re_order_level = Column(Integer, nullable = True)
    re_order_quantity = Column(Integer, nullable = True)

    inventory = relationship("Inventory")
    food = relationship("Food")
    good = relationship("Goods")

# The shopping list or order with access to a group
class ShoppingOrder(Base):
    __tablename__ = 'shopping_orders'
    id = Column(Integer, primary_key = True)
    creator_id = Column(Integer,ForeignKey('users.id'), nullable = False)
    user_group_id = Column(Integer,ForeignKey('user_groups.id'), nullable = False)

    creator = relationship("User")
    user_group = relationship("UserGroup")


# Items on a shopping list that must be bought / ordered
class ShoppingOrderItem(Base):
    __tablename__ = 'shopping_order_items'
    id = Column(Integer, primary_key = True)
    shopping_order_id = Column(Integer, ForeignKey('shopping_orders.id'))
    food_id = Column(Integer, ForeignKey('foods.id'), nullable = True)
    good_id = Column(Integer, ForeignKey('goods.id'), nullable = True)
    quantity = Column(Float, nullable = True)
    quantity_uom = Column(String(5), ForeignKey('units_of_measures.uom'), nullable = True)
    checkOff = Column(Boolean, default = False)
    item_photo = Column(String, nullable = True)
    barcode_photo = Column(String, nullable = True)
    ingredients_photo = Column(String, nullable = True)
    trade_item_id = Column(Integer, ForeignKey('trade_items.id'), nullable = True)

    food = relationship("Food")
    good = relationship("Goods")
    shopping_order = relationship("ShoppingOrder")
    trade_item = relationship("TradeItem")


# Items that relate to real products bought in the retail / grocery stores
class TradeItem(Base):
    __tablename__ = 'trade_items'
    id = Column(Integer, primary_key = True)
    ean = Column(String(13), nullable = True)
    upc = Column(String(13), nullable = True)
    gtin = Column(String(14), nullable = True)
    titleEN = Column(String(80), nullable = False)
    titleDE = Column(String(80), nullable = True)

####### insert at end of file #######

#engine = create_engine('postgresql://vagrant:vagrant@127.0.0.1:5432/np')
engine = create_engine('postgres://njxqkgsvotldpo:0091ec1051866196d42e608aadc421ef9bb58c37d9fcfe0e7bac4e9ce63929f8@ec2-54-228-182-57.eu-west-1.compute.amazonaws.com:5432/ddjblvctcusagj')

# TODO: Ensure that drop cascade works or try to use SQLAlchemy-Migrate
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
