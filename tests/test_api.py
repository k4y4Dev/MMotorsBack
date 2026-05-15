from sqlalchemy.orm import Session, declarative_base, Mapped, mapped_column







def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello":"Test deploy CI/CD"}

# def test_read_items():
#     response = client.get("/items")
#     assert response.status_code == 200
#     assert response.json() == {"Hello":"Test deploy CI/CD"}


def test_create_car(admin_client):
    response = admin_client.post(
        "/api/cars", json={
            "name": "Test Car", "price": 333, "km": 333, "image": "test.jpg"
        }
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == "Test Car"
    assert data["price"] == 333
    assert data["km"] == 333
    assert data["image"] == "test.jpg"
    assert "id" in data
