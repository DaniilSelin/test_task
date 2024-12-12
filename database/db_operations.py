from pymongo import MongoClient
from .config import Config
from .connection import initialize_database_connection


MONGO_CLIENT, MONGO_DB = initialize_database_connection()


def create_form_template(template_data):
    collection = MONGO_DB[Config.MONGO_COLLECTION_NAME]
    result = collection.insert_one(template_data)
    return result.inserted_id


def get_all_form_templates():
    collection = MONGO_DB[Config.MONGO_COLLECTION_NAME]
    return list(collection.find({}))


def find_matching_template(form_fields):
    collection = MONGO_DB[Config.MONGO_COLLECTION_NAME]
    # Логика поиска подходящего шаблона
    for template in collection.find({}):
        if all(field in form_fields.items() for field in template.items()):
            return template['name']
    return None
