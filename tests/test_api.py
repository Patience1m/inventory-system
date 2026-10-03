from app import create_app

app = create_app("testing")

def test_get_all_items():
    client = app.test_client()
    response = client.get("/inventory")
    assert response.status_code == 200
    assert len(response.get_json()["data"]) == 3

def test_get_one_item():
    client = app.test_client()
    response = client.get("/inventory/1")
    assert response.status_code == 200
    assert response.get_json()["data"]["product_name"] == "Nutella"

def test_get_one_item_not_found():
    client = app.test_client()
    response = client.get("/inventory/99")
    assert response.status_code == 404

def test_create_item():
    client = app.test_client()
    response = client.post("/inventory", json={"product_name": "Milk", "price": 1.2, "stock": 5})
    assert response.status_code == 201
    data = response.get_json()["data"]
    assert "id" in data and data["product_name"] == "Milk"
    assert len(client.get("/inventory").get_json()["data"]) == 4

def test_create_item_missing_name():
    client = app.test_client()
    response = client.post("/inventory", json={"price": 1})
    assert response.status_code == 422

def test_create_item_bad_price():
    client = app.test_client()
    response = client.post("/inventory", json={"product_name": "X", "price": "free"})
    assert response.status_code == 422

def test_create_item_no_body():
    client = app.test_client()
    response = client.post("/inventory")
    assert response.status_code == 422

def test_create_item_unknown_field():
    client = app.test_client()
    response = client.post("/inventory", json={"product_name": "X", "color": "red"})
    assert response.status_code == 422

def test_update_item():
    client = app.test_client()
    response = client.patch("/inventory/1", json={"price": 9.99, "stock": 7})
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["price"] == 9.99 and data["stock"] == 7
    assert data["product_name"] == "Nutella"

def test_update_item_not_found():
    client = app.test_client()
    response = client.patch("/inventory/99", json={"price": 1})
    assert response.status_code == 404

def test_update_item_invalid_stock():
    client = app.test_client()
    response = client.patch("/inventory/1", json={"stock": -3})
    assert response.status_code == 422

def test_update_item_cannot_change_id():
    client = app.test_client()
    response = client.patch("/inventory/1", json={"id": 50})
    assert response.status_code == 422

def test_delete_item():
    client = app.test_client()
    response = client.delete("/inventory/2")
    assert response.status_code == 204
    assert client.get("/inventory/2").status_code == 404

def test_delete_item_not_found():
    client = app.test_client()
    response = client.delete("/inventory/99")
    assert response.status_code == 404