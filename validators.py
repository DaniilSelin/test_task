import re
from datetime import datetime

"""
Были мысли воспользоваться pydantic, 
 но в силу тривиальности задачи отказался от этой идеи.
"""

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
PHONE_REGEX = r'^\+7 \d{3} \d{3} \d{2} \d{2}$'
DATE_REGEX = r'^(\d{2}\.\d{2}\.\d{4}|\d{4}-\d{2}-\d{2})$'


def validate_field(field_value):
    """
    Функция для валидации поля в зависимости от типа.
    Если валидация не проходит для указанного типа, пробует
    последовательно 'date', 'phone', 'email', и в итоге 'text'.

    Args:
        field_value (str): поле формы.

    Returns:
        type_: Тип присланного поля.
    """
    # Последовательность проверки типов
    types_order = ["date", "phone", "email"]
    # Валидаторы для типов
    validators = {
        "email": validate_email,
        "phone": validate_phone,
        "date": validate_date
    }
    for type_ in types_order:
        if validators[type_](field_value):
            return type_
    return "text"


def validate_email(email: str) -> bool:
    """
    Валидация email.

    :args:
        email (str): Email адрес для проверки.

    :returns:
        bool: True если формат валиден, False иначе.
    """
    if not isinstance(email, str):
        return False
    if not re.fullmatch(EMAIL_REGEX, email):
        return False
    return True


def validate_phone(phone: str) -> bool:
    """
    Валидация номера телефона в формате +7 XXX XXX XX XX.

   :args:
        phone (str): Номер телефона для проверки.

    :returns:
        bool: True если формат валиден, False иначе.
    """
    if not isinstance(phone, str):
        return False
    if not re.fullmatch(PHONE_REGEX, phone):
        return False
    return True


def validate_date(date: str) -> bool:
    """
    Валидация даты в форматах DD.MM.YYYY и YYYY-MM-DD.

    :args:
        date (str): Дата для проверки.

    :returns:
        bool: True если формат валиден, False иначе.
    """
    if not isinstance(date, str):
        return False

    if not re.fullmatch(DATE_REGEX, date):
        return False

    # Попытка распарсить дату в обоих форматах
    for date_format in ('%d.%m.%Y', '%Y-%m-%d'):
        try:
            datetime.strptime(date, date_format)
            return True
        except ValueError:
            continue

    return False