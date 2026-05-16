

def test_get_all_cars(client):
    response = client.get("/api/cars")
    assert response.status_code == 200

    response = client.get("/api/car")
    assert response.status_code == 404


def test_get_car(admin_client, client):
    admin_client.post(
        "/api/cars",
        json={"name": "Test Car", "price": 333, "km": 333, "image": "test.jpg"},
    )
    response = client.get("/api/cars/1")
    assert response.status_code == 200

    response = client.get("/api/cars/999")
    assert response.status_code == 404

    response = client.get("/api/cars/a")
    assert response.status_code == 422

def test_create_car_fail(client):
    # 1. Non Authenticated → 401
    response = client.post(
        "/api/cars",
        json={"name": "Test Car", "price": 333, "km": 333, "image": "test.jpg"},
    )
    assert response.status_code == 401, response.text
    
def test_create_car_nonadmin_fail(auth_client):
    # 2. Authentifié mais pas admin → 403
    response = auth_client.post(
        "/api/cars",
        json={"name": "Test Car", "price": 333, "km": 333, "image": "test.jpg"},
    )
    assert response.status_code == 403, response.text
    

def test_create_car( admin_client):

    # 3. Admin → 201
    response = admin_client.post(
        "/api/cars",
        json={"name": "Test Car", "price": 333, "km": 333, "image": "test.jpg"},
    )
    assert response.status_code == 201, response.text

    # 4. Payload invalide → 422
    response = admin_client.post(
        "/api/cars",
        json={"name": "Test Car", "price": 333, "km": 333},  # image manquante
    )
    assert response.status_code == 422, response.text


def test_delete_car(admin_client):
    admin_client.post(
        "/api/cars",
        json={"name": "Test Car", "price": 333, "km": 333, "image": "test.jpg"},
    )
    response = admin_client.delete("/api/cars/1")
    assert response.status_code == 204, response.text

    response = admin_client.delete("/api/cars/999")
    assert response.status_code == 404, response.text


def test_put_car(admin_client):
    admin_client.post(
        "/api/cars",
        json={"name": "Test Car", "price": 333, "km": 333, "image": "test.jpg"},
    )
    response = admin_client.put("/api/cars/999")
    assert response.status_code == 422, response.text

    response = admin_client.put(
        "/api/cars/1",
        json={"name": "Test Car Modified", "price": 666, "km": 666, "image": "test2.jpg"},
    )
    assert response.status_code == 200, response.text

    response = admin_client.put(
        "/api/cars/1",
        json={"name": "Test Car Modified"},  # champs requis manquants
    )
    assert response.status_code == 422, response.text



def test_patch_car(admin_client):
    admin_client.post(
        "/api/cars",
        json={"name": "Test Car", "price": 333, "km": 333, "image": "test.jpg"},
    )
    response = admin_client.patch("/api/cars/999")
    assert response.status_code == 422, response.text

    response = admin_client.patch(
        "/api/cars/1",
        json={"name": "Test Car Modified", "price": 666, "km": 666, "image": "test2.jpg"},
    )
    assert response.status_code == 200, response.text

    response = admin_client.patch(
        "/api/cars/1",
        json={"name": "Test Car Modified"},  # champs requis manquants
    )
    assert response.status_code == 200, response.text