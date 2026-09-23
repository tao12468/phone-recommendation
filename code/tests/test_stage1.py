from app import app


client = app.test_client()


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["stage"] == 1


def test_phones():
    response = client.get("/api/phones")
    assert response.status_code == 200
    data = response.get_json()
    assert data["total"] == 10
    assert len(data["items"]) == 10


def test_phone_detail():
    response = client.get("/api/phones/1")
    assert response.status_code == 200
    assert response.get_json()["name"] == "小米 14"


def test_phone_detail_not_found():
    response = client.get("/api/phones/999")
    assert response.status_code == 404


def test_recommendations_cold_start():
    response = client.get("/api/recommendations")
    assert response.status_code == 200
    data = response.get_json()
    assert data["strategy"] == "simple_content_based"
    assert len(data["items"]) == 5


def test_recommendations_with_preferences():
    response = client.get(
        "/api/recommendations?budget=4000&brand=小米,苹果&scene=游戏,拍照"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["items"]) >= 1
    assert "score" in data["items"][0]
