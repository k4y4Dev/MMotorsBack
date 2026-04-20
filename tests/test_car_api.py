from .conftest import client

def test_get_all_cars():
    response = client.get("/api/cars")
    assert response.status_code == 200

def test_get_car():
    client.post(
        "/api/cars", json={
            "name": "Test Car", "price": 333, "km": 333, "image": "test.jpg"
        }
    )

    response = client.get("/api/cars/1")
    assert response.status_code == 200

    response = client.get("/api/cars/2")
    assert response.status_code == 404
    
    response = client.get("/api/cars/a")
    assert response.status_code == 422




def test_create_car():
    response = client.post(
        "/api/cars", json={
            "name": "Test Car", "price": 333, "km": 333, "image": "test.jpg"
        }
    )

    assert response.status_code == 201, response.text

    response = client.post(
        "/api/cars", json={
            "name": "Test Car", "price": 333, "km": 333
        }
    )

    assert response.status_code == 422, response.text
    
    response = client.post(
        "/api/cars", json={
            "name": "Test Car", "price": "333", "km": 333
        }
    )

    assert response.status_code == 422, response.text

def test_delete_car():
    response = client.post(
        "/api/cars", json={
            "name": "Test Car", "price": 333, "km": 333, "image": "test.jpg"
        }
    )

    assert response.status_code == 201, response.text

    response = client.delete("/api/cars/1")
    assert response.status_code == 204, response.text

    response = client.delete("/api/cars/2")
    assert response.status_code == 404, response.text

