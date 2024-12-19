import pytest
import requests

BASE_URL = "http://127.0.0.1:5000"


# запускается ровно один раз перед тестами get_form
@pytest.fixture(scope="session", autouse=True)
def setup_templates():
    """Очистка базы данных и создание шаблонов."""
    # Очистка базы данных
    response = requests.post(f"{BASE_URL}/clear_db")
    assert response.status_code == 200

    # Шаблоны для тестов, копипаст из test_create
    templates = [
        {
            "name": "User Registration",
            "fields": [
                {"name": "email", "type": "email"},
                {"name": "phone", "type": "phone"},
                {"name": "dob", "type": "date"},
            ],
        },
        {
            "name": "Contact Form",
            "fields": [
                {"name": "name", "type": "text"},
                {"name": "email", "type": "email"},
                {"name": "message", "type": "text"},
            ],
        },
        {
            "name": "Event Creation",
            "fields": [
                {"name": "title", "type": "text"},
                {"name": "description", "type": "text"},
                {"name": "date", "type": "date"},
            ],
        },
        {
            "name": "Simple Form",
            "fields": [{"name": "info", "type": "text"}],
        },
    ]

    for template in templates:
        response = requests.post(
            f"{BASE_URL}/create_template",
            json=template,
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 201
