# Imports the Google Cloud client library
from google.cloud import translate

#translate_client = translate.from_service_account_json(r'C:\Users\Soeren\Google Drive\Projekte\Account Keys\My First Project-297eb489437d.json')
client = translate.Client(target_language='en')
# detect Language
result = client.translate("Zwiebel")
print(result['detectedSourceLanguage'])
print(result['translatedText'])
