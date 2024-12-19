import pytest
import requests
from eKom.test.test_setup import BASE_URL


def test_get_form_user_registration():
    """Тест для формы 'User Registration'."""
    data = {
        "email": "user@example.com",
        "phone": "+123456789",
        "dob": "1990-01-01"
    }
    response = requests.post(f"{BASE_URL}/get_form", json=data)
    assert response.status_code == 200
    assert response.json().get("matching_template_name") == "User Registration"


def test_get_form_contact_form():
    """Тест для формы 'Contact Form'."""
    data = {
        "name": "John Doe",
        "email": "contact@example.com",
        "message": "This is a test message."
    }
    response = requests.post(f"{BASE_URL}/get_form", json=data)
    assert response.status_code == 200
    assert response.json().get("matching_template_name") == "Contact Form"


def test_get_form_event_creation():
    """Тест для формы 'Event Creation'."""
    data = {
        "title": "Team Meeting",
        "description": "Discuss project progress."
    }
    response = requests.post(f"{BASE_URL}/get_form", json=data)
    assert response.status_code == 200
    assert response.json().get("matching_template_name") == "Event Creation"


def test_get_form_no_match():
    """Тест для случая, когда подходящей формы нет."""
    data = {
        "unknown_field": "some value"
    }
    response = requests.post(f"{BASE_URL}/get_form", json=data)
    assert response.status_code == 404
    result = response.json()
    assert result.get("matching_template_name") is None
    assert isinstance(result, dict)
    assert "unknown_field" in result
    assert result["unknown_field"] == "text"