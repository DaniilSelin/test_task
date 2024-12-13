from flask import Flask, request, jsonify
from models import validate_email, validate_phone, validate_date
from database.db_operations import create_form_template, get_all_form_templates, find_templates_by_field, build_index, clear_database

app = Flask(__name__)


def find_best_matching_template(potential_templates, form_fields):
    # Отсортируем шаблоны по убыванию количества полей в 'fields'
    sorted_templates = sorted(potential_templates, key=lambda template: len(template['fields']), reverse=True)

    # Перебираем отсортированные шаблоны
    for template in sorted_templates:
        # Проверяем, что количество полей шаблона не больше, чем в присланной форме
        if len(template['fields']) > len(form_fields):
            continue  # Пропускаем шаблон с большим количеством полей

        # Проверяем, что все поля шаблона есть в форме и типы совпадают
        all_fields_match = True
        for field_name, field_type in template['fields'].items():
            if field_name not in form_fields or not isinstance(form_fields[field_name], field_type):
                all_fields_match = False
                break

        # Если все поля совпадают, возвращаем этот шаблон как лучший
        if all_fields_match:
            return template

    # Если подходящий шаблон не найден
    return None


def validate_field(field_value):
    """
    Функция для валидации поля в зависимости от типа.
    Если валидация не проходит для указанного типа, пробует
    последовательно 'date', 'phone', 'email', и в итоге 'text'.
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


@app.route('/validate/email', methods=['POST'])
def validate_email_route():
    """
    Эндпоинт для валидации email.
    """
    data = request.json
    email = data.get("email")
    if not email:
        return jsonify({"ошибка": "Email обязателен"}), 400

    result = validate_email(email)
    return jsonify({"email": email, "is_valid": result})


@app.route('/validate/phone', methods=['POST'])
def validate_phone_route():
    """
    Эндпоинт для валидации номера телефона.
    """
    data = request.json
    phone = data.get("phone")
    if not phone:
        return jsonify({"ошибка": "Номер телефона обязателен"}), 400

    result = validate_phone(phone)
    return jsonify({"phone": phone, "is_valid": result})


@app.route('/validate/date', methods=['POST'])
def validate_date_route():
    """
    Эндпоинт для валидации даты.
    """
    data = request.json
    date = data.get("date")
    if not date:
        return jsonify({"ошибка": "Дата обязательна"}), 400

    result = validate_date(date)
    return jsonify({"date": date, "is_valid": result})


@app.route('/clear_db', methods=['POST'])
def clear_db():
    """
    Эндпоинт для очистки базы данных.
    """
    try:
        clear_database()
        return jsonify({"message": "Database cleared successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/templates', methods=['GET'])
def get_templates():
    """
    Эндпоинт для получения всех шаблонов.
    """
    templates = get_all_form_templates()

    # Преобразование ObjectId в строку
    for template in templates:
        template['_id'] = str(template['_id'])

    return jsonify(templates)


@app.route('/templates', methods=['POST'])
def create_template():
    """
    Эндпоинт для создания нового шаблона.
    """
    data = request.json
    if not data:
        return jsonify({"ошибка": "Данные шаблона обязательны"}), 400

    template_name = data.get("name")
    fields = data.get("fields")

    if not template_name:
        return jsonify({"ошибка": "Имя шаблона обязательно"}), 400
    if not fields or not isinstance(fields, list):
        return jsonify({"ошибка": "Список полей обязателен"}), 400

    warnings = []
    validated_fields = []
    valid_types = {"date", "email", "phone", "text"}

    for field in fields:
        field_name = field.get("name")
        field_type = field.get("type")

        if not field_name or not field_type:
            # Пропускаем некорректные поля
            warnings.append(f"Поле {field} не содержит имени или типа")
            continue

        if field_type not in valid_types:
            warnings.append(f"Тип поля '{field_name}' ({field_type}) некорректен. Пропущено.")
            continue

        validated_fields.append({"name": field_name, "type": field_type})
        # Обновляем индексы
        build_index(field_name, field_type, template_name)

    template_id = create_form_template({"name": template_name, "fields": validated_fields})

    return jsonify({
        "сообщение": "Шаблон создан",
        "id_шаблона": str(template_id),
        "предупреждения": warnings,
        "поля": validated_fields
    }), 201


@app.route('/get_form', methods=['POST'])
def get_form():
    """
    Эндпоинт для поиска подходящего шаблона по полям формы.
    Из подходящих выбирается шаблон с наибольшим количеством форм.
    """
    form_fields = request.json
    if not form_fields:
        return jsonify({"ошибка": "Поля формы обязательны"}), 400
    print(form_fields)
    # Хранение подходящих шаблонов
    potential_templates = set()

    result_form = {}

    # Перебираем поля формы
    for field_name, field_value in form_fields.items():
        # Валидация поля
        corrected_type = validate_field(field_value)

        result_form[field_name] = corrected_type

        # Поиск шаблонов для поля
        matching_templates = find_templates_by_field(field_name, corrected_type)

        if matching_templates:
            potential_templates.intersection_update(*matching_templates)

    # Находим самый выгодный шаблон
    best_template = find_best_matching_template(potential_templates, form_fields)

    # Если потенциальные шаблоны найдены, возвращаем самый "выгодный" из них
    if best_template:
        return jsonify({"Имя подходящего шаблона": best_template["name"]})

    # Если не нашли подходящий шаблон, возвращаем необработанные поля
    return jsonify(result_form), 404


if __name__ == '__main__':
    app.run(debug=True)