import foods
import ndb
from googletrans import Translator


def loadFile(file_name):
    newFile = open(file_name)
    file_content = newFile.read()
    newFile.close
    return file_content

def createListFromText(some_String, some_RecordDelimiter, some_FieldDelimiter):
    newList = [s.strip().split(some_FieldDelimiter) for s in some_String.split(some_RecordDelimiter)]
    print(newList)
    return newList

def GetNutritionDataFromNDB(some_food):
    """Account Email: mailboxsoeren@gmail.com
    Account ID: 738eae59-c15d-4b89-a621-bcd7182a51e2"""
    KEY = "ZQfrfyBrTTa3uEt8ooC9yZzmv5WNzgoJOlj6roBz"
    n = ndb.NDB(KEY)

    """ Search Database and return all results in a Dictionary """
    results = n.search_keyword(some_food)
    #print("Dictionary = ")
    print(results)

    """ From all results take first one """

    for item in results['items']:
        print(item)

    """ similar to
    https://api.nal.usda.gov/ndb/search/?format=json&q=pepper&sort=n&max=200&offset=0&api_key=DEMO_KEY&ds=Standard%20Reference """
    Enhance def search_keyword in class NDB to accomodate "ds=Standard%Reference"

    resultsRelevantItem = list(results['items'])[0]
    print resultsRelevantItem

    """ Creates a food report object for item using ndb Number """
    report = n.food_report(resultsRelevantItem.get_ndbno())
    #print(report)

    """ Get value of first nutrient object (energy) within food report list of nutrients """
    NutrientObject = report['food'].get_nutrients()[0]
    NutritionObjectItems = NutrientObject.get_value()
    print(NutrientObject.get_value())
    print(NutrientObject.get_measures())

def detect_language(text):
    """Detects the text's language."""
    translate_client = Translator()

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.detect_language(text)

    print('Text: {}'.format(text))
    print('Confidence: {}'.format(result['confidence']))
    print('Language: {}'.format(result['language']))


""" Loading a textfile with a comma separated recipe and storing this in a list of objects """
FileName = r"C:\Users\Soeren\Google Drive\Soeren\Projekte\Pyhton Fundamentals\food_log\recipe.txt"
content = loadFile(FileName)
recipe_list = content.split(",")
ingredients = []
counterX = 0
for i in recipe_list:
    print("Ingredient "+str(counterX)+" = " + i)
    elements = i.split()     
    new_ingredient = foods.Ingredient(elements[0],elements[1],elements[2])
    ingredients.append(new_ingredient)
    counterX = counterX + 1

#print(ingredients[4].name + " " + ingredients[4].uom + " " + ingredients[4].units)
                                
""" Loading a textfile with space delimted rules for a nutrition plan """
FileName = r"C:\Users\Soeren\Google Drive\Soeren\Projekte\Pyhton Fundamentals\food_log\nutrition_plan.txt"
content = loadFile(FileName)
plan_rules = [s.strip().split() for s in content.splitlines()]
#plan_rules = createListFromText(content,"\n"," ")

rules = []
counterX = 0
for r in plan_rules:
    print("Rule "+str(counterX)+" = "+"|".join(r))
    new_rule = foods.NutritionPlanItem(r[0],r[1],r[2],r[3],r[4])
    rules.append(new_rule)
    counterX = counterX + 1

#print(rules[3].min_limit)

""" Trasnlate German to English """
ingredientDE = ingredients[6].name
translate_client = Translator()
result = translate_client.translate(ingredientDE, dest="en", src="de")
searchTermEN = result.pronunciation
print("Deutsch = "+ingredientDE)
print("Englisch = "+searchTermEN)

""" Get Nutrient (Energy) from NDB """
GetNutritionDataFromNDB(searchTermEN)

