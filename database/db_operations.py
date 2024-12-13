from pymongo import MongoClient
from .config import Config
from .connection import initialize_database_connection


MONGO_CLIENT, MONGO_DB = initialize_database_connection()


def build_index(field_name, field_type, template_name):
    # Комбинируем имя поля и тип
    key = f"{field_name}+{field_type}"
    index = MONGO_DB[Config.INDEX_COLLECTION_NAME]

    existing_index = index.find_one({"key": key})

    if existing_index:
        # Если индекс уже существует, добавляем имя шаблона, если его там нет
        if template_name not in existing_index['templates']:
            index.update_one(
                {"key": key},
                {"$push": {"templates": template_name}}
            )
    else:
        # Если индекса нет, создаем новый
        index.insert_one({"key": key, "templates": [template_name]})


def find_templates_by_field(field_name, field_type):
    """
    Поиск всех шаблонов, содержащих указанное поле с данным типом.
    """
    index = MONGO_DB[Config.INDEX_COLLECTION_NAME]
    key = f"{field_name}+{field_type}"
    result = index.find_one({"key": key})
    return result['templates'] if result else []


def create_form_template(template_data):
    collection = MONGO_DB[Config.MONGO_COLLECTION_NAME]
    result = collection.insert_one(template_data)
    return result.inserted_id


def get_all_form_templates():
    collection = MONGO_DB[Config.MONGO_COLLECTION_NAME]
    return list(collection.find({}))


def clear_database():
    """
    Удаляет все данные из коллекций, связанных с шаблонами и индексами.
    """
    # Очистка коллекции шаблонов
    template_collection = MONGO_DB[Config.MONGO_COLLECTION_NAME]
    template_collection.delete_many({})

    # Очистка коллекции индексов
    index_collection = MONGO_DB[Config.INDEX_COLLECTION_NAME]
    index_collection.delete_many({})