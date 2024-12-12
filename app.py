from flask import Flask, request, jsonify
from models import validate_email, validate_phone, validate_date
from database.db_operations import create_form_template, get_all_form_templates, find_matching_template

app = Flask(__name__)


@app.route('/validate/email', methods=['POST'])
def validate_email_route():
    """
    Эндпоинт для валидации email.
    """
    data = request.json
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400

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
        return jsonify({"error": "Phone number is required"}), 400

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
        return jsonify({"error": "Date is required"}), 400

    result = validate_date(date)
    return jsonify({"date": date, "is_valid": result})


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
        return jsonify({"error": "Template data is required"}), 400

    template_id = create_form_template(data)
    return jsonify({"message": "Template created", "template_id": str(template_id)}), 201


@app.route('/templates/match', methods=['POST'])
def match_template():
    """
    Эндпоинт для поиска подходящего шаблона по полям формы.
    """
    form_fields = request.json
    if not form_fields:
        return jsonify({"error": "Form fields are required"}), 400

    template_name = find_matching_template(form_fields)
    if template_name:
        return jsonify({"template_name": template_name})
    else:
        return jsonify({"message": "No matching template found"}), 404


if __name__ == '__main__':
    app.run(debug=True)
