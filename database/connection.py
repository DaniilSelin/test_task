from pymongo import MongoClient
from eKom.database.config import Config
import time
from dotenv import load_dotenv
import os
from eKom.logging_form import logger
from pymongo.errors import ServerSelectionTimeoutError

# Загрузка переменных из .env
load_dotenv()


def connect_to_database(max_retries, delay):
    """
    Подключение к MongoDB с повторной попыткой в случае неудачи.
    """
    attempts = 0
    while attempts < max_retries:
        try:
            client = MongoClient(Config.MONGO_URI)
            db = client[Config.MONGO_DB_NAME]
            # Проверяем подключение, вызывая команду, например, получения списка коллекций
            db.list_collection_names()
            logger.info(" Подключение к MongoDB успешно! ")
            return client, db
        except ServerSelectionTimeoutError as e:
            attempts += 1
            logger.info(f" Ошибка подключения к MongoDB (попытка {attempts}/{max_retries}): {e} ")
            time.sleep(delay)
        except Exception as e:
            attempts += 1
            logger.info(f" Неизвестная ошибка при подключении к MongoDB: {e} ")
            time.sleep(delay)

    raise Exception("Не удалось подключиться к MongoDB.")


def initialize_collection(db):
    """
    Создает коллекцию для шаблонов форм и индексов, если они еще не существуют.
    """
    if Config.MONGO_COLLECTION_NAME not in db.list_collection_names():
        db.create_collection(Config.MONGO_COLLECTION_NAME)
        logger.info(f" Коллекция '{Config.MONGO_COLLECTION_NAME}' создана.")
    if Config.INDEX_COLLECTION_NAME not in db.list_collection_names():
        db.create_collection(Config.INDEX_COLLECTION_NAME)
        logger.info(f" Коллекция '{Config.INDEX_COLLECTION_NAME}' создана.")


def initialize_database_connection():
    """
    Подключение к базе данных и инициализация коллекций.

    :returns:
        MONGO_CLIENT: Объект клиента MongoDB.
        MONGO_DB: Объект базы данных MongoDB.

    :exception:
        Генерирует исключение, если подключение не удалось.
    """
    try:
        max_retries = int(os.getenv("MAX_RETRY_CONNECT_DB", 5))
        delay = int(os.getenv("TIME_SLEEP_RETRY", 5))
        MONGO_CLIENT, MONGO_DB = connect_to_database(max_retries, delay)
        initialize_collection(MONGO_DB)
        return MONGO_CLIENT, MONGO_DB
    except Exception as e:
        logger.info(f" Критическая ошибка: {e} ")
        raise