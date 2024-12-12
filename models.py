import re
from datetime import datetime
"""
Были мысли воспользоваться pydantic, 
 но в силу тривиальности задачи отказался от этой идеи.
"""

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
PHONE_REGEX = r'^\+7 \d{3} \d{3} \d{2} \d{2}$'
DATE_REGEX = r'^(\d{2}\.\d{2}\.\d{4}|\d{4}-\d{2}-\d{2})$'

def validate_email(email: str) -> bool:
    """
    Валидация email.

    Args:
        email (str): Email адрес для проверки.

    Returns:
        bool: True если формат валиден, False иначе.
    """
    if not isinstance(email, str):
        print("Передан не строковый тип")
        return False
    if not re.fullmatch(EMAIL_REGEX, email):
        print("Email формат некорректен")
        return False
    print("Формат валиден")
    return True

def validate_phone(phone: str) -> bool:
    """
    Валидация номера телефона в формате +7 XXX XXX XX XX.

    Args:
        phone (str): Номер телефона для проверки.

    Returns:
        bool: True если формат валиден, False иначе.
    """
    if not isinstance(phone, str):
        print("Передан не строковый тип")
        return False
    if not re.fullmatch(PHONE_REGEX, phone):
        print("Формат номера телефона некорректен")
        return False
    print("Телефон валиден")
    return True


def validate_date(date: str) -> bool:
    """
    Валидация даты в форматах DD.MM.YYYY и YYYY-MM-DD.

    Args:
        date (str): Дата для проверки.

    Returns:
        bool: True если формат валиден, False иначе.
    """
    if not isinstance(date, str):
        print("Передан не строковый тип")
        return False

    if not re.fullmatch(DATE_REGEX, date):
        print("Дата не соответствует ожидаемому формату")
        return False

    # Попытка распарсить дату в обоих форматах
    for date_format in ('%d.%m.%Y', '%Y-%m-%d'):
        try:
            datetime.strptime(date, date_format)
            print("Формат даты валиден")
            return True
        except ValueError:
            continue

    print("Дата не соответствует ни одному из поддерживаемых форматов")
    return False