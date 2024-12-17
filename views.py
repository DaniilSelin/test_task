from flask import Blueprint, request, jsonify
from eKom.validators import validate_field, validate_email, validate_phone, validate_date
from eKom.database.db_operations import create_form_template, get_all_form_indexes, get_all_form_templates, find_templates_by_field, build_index, clear_database
from eKom.logging_form import logger
from pymongo.errors import OperationFailure, DuplicateKeyError
from functools import wraps

views_blueprint = Blueprint('auth', __name__)


def log_requests_and_responses(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        request_info = f"URL: {request.url} | Method: {request.method} | IP: {request.remote_addr}"
        try:
            response = func(*args, **kwargs)
            status_code = response[1] if isinstance(response, tuple) else response.status_code
            logger.info(f"{request_info} | Status: {status_code}")
            return response
        except Exception as e:
            logger.error(f"{request_info} | Error: {str(e)}")
            raise
    return wrapper


def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except OperationFailure as e:
            logger.error(f"MongoDB error: {str(e)}")
            return jsonify({'error': 'Database error', 'message': str(e)}), 500
        except DuplicateKeyError as e:
            logger.warning(f"Duplicate key error: {str(e)}")
            return jsonify({'error': 'Duplicate key error', 'message': str(e)}), 400
        except Exception as e:
            logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
            return jsonify({'error': 'Unexpected error occurred', 'message': str(e)}), 500
    return wrapper


def check_fields(matching_template, form_fields):
    if len(matching_template['fields']) > len(form_fields):
        return False

    # Проверяем, что все поля шаблона есть в форме и типы совпадают
    all_fields_match = True

    for field in matching_template['fields']:

        # Проверяем наличие поля в форме и соответствие типов
        if field['name'] not in form_fields or form_fields[field['name']] != field['type']:
            all_fields_match = False
            break

    # Если все поля совпадают, возвращаем этот шаблон как лучший
    if all_fields_match:
        return True


@views_blueprint.route('/validate/email', methods=['POST'])
@log_requests_and_responses
@handle_exceptions
def validate_email_route():
    """
    Эндпоинт для проверки валидности email-адреса.

    Требования:
        email (string): Email для проверки.

    Возвращает:
        200: JSON объект { "email": <email>, "is_valid": <bool> }
        400: JSON объект { "error": "Email is required" }
    """
    data = request.json
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400

    result = validate_email(email)
    return jsonify({"email": email, "is_valid": result})


@views_blueprint.route('/validate/phone', methods=['POST'])
@log_requests_and_responses
@handle_exceptions
def validate_phone_route():
    """
    Эндпоинт для проверки валидности номера телефона.

    Требования:
        phone (string): Номер телефона для проверки.

    Возвращает:
        200: JSON объект { "phone": <phone>, "is_valid": <bool> }
        400: JSON объект { "error": "Phone number is required" }
    """
    data = request.json
    phone = data.get("phone")
    if not phone:
        return jsonify({"error": "Phone number is required"}), 400

    result = validate_phone(phone)
    return jsonify({"phone": phone, "is_valid": result})


@views_blueprint.route('/validate/date', methods=['POST'])
@log_requests_and_responses
@handle_exceptions
def validate_date_route():
    """
    Эндпоинт для проверки валидности даты.

    Требования:
        date (string): Дата для проверки.

    Возвращает:
        200: JSON объект { "date": <date>, "is_valid": <bool> }
        400: JSON объект { "error": "Date is required" }
    """
    data = request.json
    date = data.get("date")
    if not date:
        return jsonify({"error": "Date is required"}), 400

    result = validate_date(date)
    return jsonify({"date": date, "is_valid": result})


@views_blueprint.route('/clear_db', methods=['POST'])
@log_requests_and_responses
@handle_exceptions
def clear_db():
    """
    Эндпоинт для очистки базы данных.
    """
    try:
        clear_database()
        return jsonify({"message": "Database cleared successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@views_blueprint.route('/templates', methods=['GET'])
@log_requests_and_responses
@handle_exceptions
def get_templates():
    """
    Эндпоинт для получения всех шаблонов.
    """
    templates = get_all_form_templates()

    # Преобразование ObjectId в строку
    for template in templates:
        template['_id'] = str(template['_id'])

    return jsonify(templates)


@views_blueprint.route('/indexes', methods=['GET'])
@log_requests_and_responses
@handle_exceptions
def get_indexes():
    """
    Эндпоинт для получения всех индексов.
    """
    indexes = get_all_form_indexes()

    # Преобразование ObjectId в строку
    for index in indexes:
        index['_id'] = str(index['_id'])

    return jsonify(indexes)


@views_blueprint.route('/create_template', methods=['POST'])
@log_requests_and_responses
@handle_exceptions
def create_template():
    """
    Эндпоинт для создания нового шаблона.

    Требования:
        name (string): Имя шаблона.
        fields (array): Список объектов полей { "name": <string>, "type": <string> }.

    Возвращает:
        201: JSON объект с подтверждением создания
    """
    data = request.json
    if not data:
        return jsonify({"error": "Template data is required"}), 400

    template_name = data.get("name")
    fields = data.get("fields")

    if not template_name:
        return jsonify({"error": "Template name is required"}), 400
    if not fields or not isinstance(fields, list):
        return jsonify({"error": "Field list is required"}), 400

    warnings = []
    validated_fields = []
    valid_types = {"date", "email", "phone", "text"}

    for field in fields:
        field_name = field.get("name")
        field_type = field.get("type")

        if not field_name or not field_type:
            # Пропускаем некорректные поля
            warnings.append(f"Field {field} is missing a name or type")
            continue

        if field_type not in valid_types:
            warnings.append(f"Field '{field_name}' has an invalid type ({field_type}). Skipped.")
            continue

        validated_fields.append({"name": field_name, "type": field_type})
        # Обновляем индексы
        build_index(field_name, field_type, {"name": template_name, "fields": validated_fields})

    template_id = create_form_template({"name": template_name, "fields": validated_fields})

    return jsonify({
        "message": "Template created",
        "template_id": str(template_id),
        "warnings": warnings,
        "fields": validated_fields
    }), 201


@views_blueprint.route('/get_form', methods=['POST'])
@log_requests_and_responses
@handle_exceptions
def get_form():
    """
    Эндпоинт для поиска подходящего шаблона по полям формы.

    Требования:
        JSON объект с полями формы: { "<field_name>": <value> }.

    Возвращает:
        200: JSON объект { "matching_template_name": <template_name> }, если найден подходящий шаблон.
        404: JSON объект с обработанными полями формы, если шаблон не найден.
        400: Если поля формы отсутствуют.
    """
    form_fields = request.json
    if not form_fields:
        return jsonify({"error": "Form fields are required"}), 400

    # Хранение имен шаблонов для уникальности
    template_names = set()

    potential_template_name = ""
    # Зранение количества полей текущего 'лучшего' шаблона
    max_count_fields = 0

    result_form = {}

    # Перебираем поля формы
    for field_name, field_value in form_fields.items():
        # Валидация полей
        corrected_type = validate_field(field_value)

        result_form[field_name] = corrected_type

    for field_name, field_type in result_form.items():
        # Поиск шаблонов
        matching_templates = find_templates_by_field(field_name, field_type)

        if matching_templates:
            for template in matching_templates:
                # Проверяем уникальность имени шаблона и количество его полей
                if (template["name"] not in template_names
                        and len(template["fields"]) > max_count_fields):

                    template_names.add(template["name"])
                    if check_fields(template, result_form):
                        # обновляем результат
                        potential_template_name = template["name"]
                        max_count_fields = len(template["fields"])

    # Если подходящий шаблон найден, возвращаем его
    if potential_template_name:
        return jsonify({"matching_template_name": potential_template_name})

    # Если не нашли подходящий шаблон, возвращаем обработанные поля
    return jsonify(result_form), 404
