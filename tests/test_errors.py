from unittest.mock import patch


def assert_message(response, expected_substring, status_code):
    assert response.status_code == status_code
    data = response.get_json()
    assert "message" in data
    assert expected_substring in data["message"]


# -------------------------
# handle_xxx_error
# -------------------------
def print_error_handlers(app):
    print("Registered error handlers:")
    # _error_handler_spec maps blueprint_name (or None) to {code_or_exc: handler}
    for bp_name, handlers in app.error_handler_spec.items():
        for code_or_exc, handler in handlers.items():
            print(f"  {code_or_exc}: {handler}")


def test_handle_404_error(app):
    with app.test_client() as client:
        response = client.get("/route-not-found-404")
        assert_message(response, "Resource not found", 404)


def test_handle_runtime_error(app):
    with app.test_client() as client:
        with patch("app.routes.public_routes.Nightline.get_nightline") as mock_get_nightline:
            mock_get_nightline.side_effect = RuntimeError("Random unhandled runtime error")
            response = client.get("/public/test")
            assert_message(response, "An error occurred while processing data", 500)


def test_handle_generic_error(app):
    with app.test_client() as client:
        with patch("app.routes.public_routes.Nightline.get_nightline") as mock_get_nightline:
            mock_get_nightline.side_effect = Exception("Random unhandled server error")
            response = client.get("/public/test")
            assert_message(response, "An unexpected error occurred", 500)
