import logging
from logging.handlers import RotatingFileHandler
import os


# Создаем папку для логов
log_directory = "log"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Настройка логгера
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

# Хендлер для ротации логов
log_file = os.path.join(log_directory, "service.log")
rotating_handler = RotatingFileHandler(
    log_file, maxBytes=5 * 1024 * 1024, backupCount=5  # 5 MB, 5 файлов
)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
rotating_handler.setFormatter(formatter)

# Хендлер для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Добавляем хендлеры к логгеру
logger.addHandler(rotating_handler)
logger.addHandler(console_handler)