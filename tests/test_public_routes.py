from app.models.nightline import Nightline


def assert_message(response, expected_substring, status_code):
    assert response.status_code == status_code
    data = response.get_json()
    assert "message" in data
    assert expected_substring in data["message"]


# -------------------------
# public/<nightline_name>
# -------------------------
def test_get_nightline_status_success(client):
    Nightline.add_nightline("pubroutetest")

    response = client.get("/public/pubroutetest")
    assert response.status_code == 200
    data = response.get_json()
    assert data == {
        "nightline_name": "pubroutetest",
        "status_name": "default",
        "description_de": "",
        "description_en": "",
        "description_now_de": "Wir sind jetzt erreichbar 📞",
        "description_now_en": "We're now available 📞",
        "now": False,
    }

    Nightline.remove_nightline("pubroutetest")


def test_get_nightline_status_not_found(client):
    response = client.get("/public/nonexistent")
    assert_message(response, "Nightline 'nonexistent' not found", 404)


def test_get_nightline_status_invalid_name(client):
    response = client.get("/public/..")
    assert response.status_code == 400


# -------------------------
# public/all
# -------------------------
def test_get_all_nightlines(client):
    pubroutetest1 = Nightline.add_nightline("pubroutetest1")
    pubroutetest2 = Nightline.add_nightline("pubroutetest2")
    pubroutetest2.set_status("english")
    pubroutetest2.set_now(True)
    pubroutetest3 = Nightline.add_nightline("pubroutetest3")
    pubroutetest3.set_status("german")

    resp = client.get("/public/all")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 3


def test_filter_by_status(client):
    response = client.get("/public/all?status=default")

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["status_name"] == "default"


def test_filter_by_language(client):
    response = client.get("/public/all?language=de")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["nightline_name"] == "pubroutetest3"


def test_filter_by_now_true(client):
    response = client.get("/public/all?now=true")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["now"] is True


def test_filter_by_now_false(client):
    response = client.get("/public/all?now=false")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]["now"] is False


def test_invalid_now_value_returns_400(client):
    response = client.get("/public/all?now=maybe")
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data or "message" in data

    Nightline.remove_nightline("pubroutetest1")
    Nightline.remove_nightline("pubroutetest2")
    Nightline.remove_nightline("pubroutetest3")
