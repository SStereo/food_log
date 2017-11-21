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
    title = Column(String(80), nullable = False)


class Meal(Base):
    __tablename__ = 'meals'
    id = Column(Integer, primary_key = True)
    title = Column(String(80), nullable = False)
    description = Column(String(250), nullable = True)
    portions = Column(SmallInteger, nullable = True)
    rating = Column(SmallInteger, nullable = True)
    image = Column(LargeBinary, nullable = True)
    created = Column(DateTime, default = datetime.datetime.utcnow)


class Ingredient(Base):
    __tablename__ = 'ingredients'
    id = Column(Integer, primary_key = True)
    quantity = Column(Float, nullable = False)
    uom = Column(String(5), ForeignKey('units_of_measure.uom'))
    meal_id = Column(Integer, ForeignKey('meals.id'))
    food_id = Column(Integer, ForeignKey('foods.id'))
    created = Column(DateTime, default = datetime.datetime.utcnow)

    food = relationship("Food", back_populates="ingredients")
    meal = relationship("Meal")


class Food(Base):
    __tablename__ = 'foods'
    id = Column(Integer, primary_key = True)
    title = Column(String(80), nullable = False)
    description = Column(String(250), nullable = True)
    image = Column(LargeBinary, nullable = True)

    ingredients = relationship("Ingredient", back_populates="food")


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

engine = create_engine('postgresql://vagrant:vagrant@127.0.0.1:5432/np')

Base.metadata.create_all(engine)
