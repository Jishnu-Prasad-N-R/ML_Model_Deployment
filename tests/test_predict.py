def test_predict_valid200(client, auth_headers):
    payload = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
    }

    response = client.post("/api/v1/predict", json=payload, headers=auth_headers)

    assert response.status_code == 200

    data = response.json()

    assert data["prediction"] in ["setosa", "versicolor", "virginica"]
    
    assert 0.0 <= data["confidence"] <= 1.0
    
    assert "request_id" in data


def test_predict_missing_field422(client, auth_headers):
    payload = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        # petal_width missing 
    }

    response = client.post("/api/v1/predict", json=payload, headers=auth_headers)

    assert response.status_code == 422


def test_predict_wrong_type422(client, auth_headers):
    payload = {
        "sepal_length": "banana",
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
    }

    response = client.post("/api/v1/predict", json=payload, headers=auth_headers)

    assert response.status_code == 422


def test_predict_negative422(client, auth_headers):
    payload = {
        "sepal_length": -5,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
    }

    response = client.post("/api/v1/predict", json=payload, headers=auth_headers)

    assert response.status_code == 422