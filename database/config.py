import os


class Config:
    """
    Конфигурация подключения к MongoDB
    """
    MONGO_URI = f'mongodb://{os.getenv("MONGO_DB_URL_CONNECT")}'
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'form_templates_db')
    INDEX_COLLECTION_NAME = os.getenv('INDEX_DB_NAME', 'indexes')
    MONGO_COLLECTION_NAME = os.getenv('MONGO_COLLECTION_NAME',
                                      'form_templates')
