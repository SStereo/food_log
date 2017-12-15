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
                        Boolean)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Declarative Mapping

Base = declarative_base()


class UOM(Base):
    __tablename__ = 'units_of_measure'
    uom = Column(String(5), primary_key = True)
    longEN = Column(String(80), nullable = True)
    shortDE = Column(String(5), nullable = True)
    longDE = Column(String(80), nullable = True)


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
    uom_id = Column(String(5), ForeignKey('units_of_measure.uom'), nullable = False)
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
    bls_code_part = Column(String(1), nullable = False)

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
    titleEN = Column(String(80), nullable = True)
    titleDE = Column(String(80), nullable = True)
    bls_code = Column(String(7), nullable = True)

    isBaseFood = Column(Boolean, unique=False, default=False)
    parentBaseFood = Column(Integer, ForeignKey('foods.id'), nullable = True)
    # Standard values
    uom_nutrient_value = Column(String(5), ForeignKey('units_of_measure.uom'), nullable = True)
    # Classification
    food_maingroup_id = Column(Integer, ForeignKey('food_maingroup.id'), nullable = True)
    food_subgroup_id = Column(Integer, ForeignKey('food_subgroup.id'), nullable = True)
    food_processing_type_id = Column(Integer, ForeignKey('food_processing_type.id'), nullable = True)
    food_preparation_type_id = Column(Integer, ForeignKey('food_preparation_type.id'), nullable = True)
    food_edible_weight_id = Column(Integer, ForeignKey('food_weight_reference.id'), nullable = True)

    referencedIn = relationship("Ingredient")

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
    value_uom = Column(String(5), ForeignKey('units_of_measure.uom'))  # example calories, or milligrams
    per_qty_uom = Column(String(5), ForeignKey('units_of_measure.uom')) # example per grams of quantity
    per_qty = Column(Float)  # example per 100 of uom (grams)
    value = Column(Float)


class Nutrient(Base):
    __tablename__ = 'nutrients'
    id = Column(Integer, primary_key = True)
    title = Column(String(80), nullable = False)


class ShoppingListItem(Base):
    __tablename__ = 'shopping_list_items'
    id = Column(Integer, primary_key = True)
    food_id = Column(Integer, ForeignKey('foods.id'))
    quantity = Column(Float, nullable = True)
    quantity_uom = Column(String(5), ForeignKey('units_of_measure.uom'), nullable = True)
    checkOff = Column(Boolean, default = False)

####### insert at end of file #######

#engine = create_engine('postgresql://vagrant:vagrant@127.0.0.1:5432/np')
engine = create_engine('postgres://njxqkgsvotldpo:0091ec1051866196d42e608aadc421ef9bb58c37d9fcfe0e7bac4e9ce63929f8@ec2-54-228-182-57.eu-west-1.compute.amazonaws.com:5432/ddjblvctcusagj')
Base.metadata.create_all(engine)
