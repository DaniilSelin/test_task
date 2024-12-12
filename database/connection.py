from pymongo import MongoClient
from .config import Config
import time
from dotenv import load_dotenv
import os

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
            print("Подключение к MongoDB успешно!")
            return client, db
        except errors.ServerSelectionTimeoutError as e:
            attempts += 1
            print(f"Ошибка подключения к MongoDB (попытка {attempts}/{max_retries}): {e}")
            time.sleep(delay)
        except Exception as e:
            attempts += 1
            print(f"Неизвестная ошибка при подключении к MongoDB: {e}")
            time.sleep(delay)

    raise Exception("Не удалось подключиться к MongoDB.")


def initialize_collection(db):
    """
    Создает коллекцию для шаблонов форм, если она еще не существует.
    """
    if Config.MONGO_COLLECTION_NAME not in db.list_collection_names():
        db.create_collection(Config.MONGO_COLLECTION_NAME)
        print(f"Коллекция '{Config.MONGO_COLLECTION_NAME}' создана.")


def initialize_database_connection():
    """
    Подключение к базе данных и инициализация коллекций.

    Возвращает:
        MONGO_CLIENT: Объект клиента MongoDB.
        MONGO_DB: Объект базы данных MongoDB.

    Исключения:
        Генерирует исключение, если подключение не удалось.
    """
    try:
        max_retries = int(os.getenv("MAX_RETRY_CONNECT_DB", 5))
        delay = int(os.getenv("TIME_SLEEP_RETRY", 5))
        MONGO_CLIENT, MONGO_DB = connect_to_database(max_retries, delay)
        initialize_collection(MONGO_DB)
        return MONGO_CLIENT, MONGO_DB
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        raise
