class Food():
    def __init__(self, food_name, calories_per_unit, food_category):
        self.name = food_name
        self.calories_per_unit = calories_per_unit
        self.category = food_category

class NutritionPlanItem():
    def __init__(self, name_person, food_category, food_min_limit, food_max_limit, food_limit_uom):
        self.person = name_person
        self.category = food_category
        self.min_limit = food_min_limit
        self.max_limit = food_max_limit
        self.limit_uom = food_limit_uom

class FoodLog():
    def __init__(self, log_date, log_time, log_food_category, log_person):
        self.date = log_date
        self.time = log_time
        self.food_category = log_food_category
        self.person = log_person

class Meal():
    def __init__(self, recipe):
        self.recipe = recipe
               
class Ingredient():
    def __init__(self,i_units,i_uom,i_name):
        self.units = i_units
        self.uom = i_uom
        self.name = i_name
        
