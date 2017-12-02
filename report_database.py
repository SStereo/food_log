import webbrowser
import os

from food_database import (Base,
                   UOM,
                   Meal,
                   Ingredient,
                   Food,
                   FoodComposition,
                   Nutrient,
                   ShoppingListItem)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Main HTML page header and styles
HTML_HEAD = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <link href="..\styles\main_styles.css" rel="stylesheet">
        <link href='https://fonts.googleapis.com/css?family=Architects+Daughter|Permanent+Marker' rel='stylesheet'>
        <title>Food Coach Database Contents</title>
    </head>
"""

HTML_BODY = """
<body>
<header>
  <div class="header">
    <!-- <img class="logo" src="..\images\logo.jpg" alt="Logo"> -->
    <h1>Food Coach</h1>
    <p>@SoerenStereo</p>
  </div>
  <div class="header_line"></div>
</header>
"""

meal_template = """
    <article class="meal">
    <div class="image_box">
    <img src="..\images\{meal_image}" alt="{meal_title}">
    </div>
    <h3>{meal_title}</h3>
    <div>
    <table class="ingredients">
    {ingredient_block}
    </table>
    </div>
    </article>
"""

ingredient_template = """
    <tr><td><span class="quantity">{ingredient_quantity} {ingredient_uom}</span> <span class="food">{ingredient_food_title}</span></td></tr>
"""

HTML_FOOT = """
    </body>
    </html>
"""

# Create or overwrite the output file
output_file = open('database_report.html', 'w')
rendered_content = ""

engine = create_engine('postgresql://vagrant:vagrant@127.0.0.1:5432/np')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

for meal_instance in session.query(Meal).all():
    #session.query(Meal).filter(Meal.title.like('%Dhal%')):
    meal_id = meal_instance.id
    print("Meal: ",meal_instance.id, meal_instance.title, meal_instance.portions)
    ingredient_content = ""
    meal_content = ""
    print("------ Ingredients ------")
    for instance in session.query(Ingredient).\
                    filter(Ingredient.meal_id==meal_id):
        print(instance.quantity, instance.uom.uom, instance.food.title)
        ingredient_content += ingredient_template.format(ingredient_quantity=instance.quantity,ingredient_uom=instance.uom.uom,ingredient_food_title=instance.food.title)
    meal_content = meal_template.format(meal_title=meal_instance.title,meal_image=meal_instance.image,ingredient_block=ingredient_content)
    rendered_content += meal_content
# Output the file
output_file.write(HTML_HEAD + HTML_BODY + rendered_content.encode("ascii", "xmlcharrefreplace").decode("utf-8") + HTML_FOOT)
output_file.close()

# open the output file in the browser
url = os.path.abspath(output_file.name)
webbrowser.open('file://' + url, new=2) # open in a new tab, if possible
