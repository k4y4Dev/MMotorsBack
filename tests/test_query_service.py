
from src.service.query_service import get_item_by_id, get_all, item_setter, item_updater

from .entity_test import MockBase, MockSchema



def test_get_item_by_id(db):
    response = get_item_by_id(db, MockBase, 50)
    fail_response = get_item_by_id(db, MockBase, 46)
    fail_response2 = get_item_by_id(db, MockBase, "a")
    
    assert response is not None
    assert response.id == 50
    assert response.name == "Test"
    assert response.price == 365
    
    assert fail_response is None

    assert fail_response2 is None

def test_get_all(db):
    response = get_all(db, MockBase)

    assert len(response) > 0
    assert isinstance(response, list)

def test_item_setter():
    mock = MockSchema(name="Mock-Sama", price=777)
    response = item_setter(mock, MockBase)

    assert response.name == "Mock-Sama"
    assert response.price == 777

def test_item_updater(db):
    response = get_item_by_id(db, MockBase, 50)
    assert response is not None
    assert response.name == "Test"
    assert response.price == 365

    mock_updated = MockSchema(name="Mock-Sama23", price=666)
    response_updated = item_updater(mock_updated, response)

    assert response_updated.id == 50
    assert response_updated.name == "Mock-Sama23"
    assert response_updated.price == 666


