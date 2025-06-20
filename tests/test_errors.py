from unittest.mock import patch
from app.models.nightline import Nightline

# -------------------------
# handle_xxx_error
# -------------------------
def print_error_handlers(app):
    print("Registered error handlers:")
    # _error_handler_spec maps blueprint_name (or None) to {code_or_exc: handler}
    for bp_name, handlers in app.error_handler_spec.items():
        bp_display = bp_name or "global"
        print(f"Blueprint: {bp_display}")
        for code_or_exc, handler in handlers.items():
            print(f"  {code_or_exc}: {handler}")

def test_handle_404_error(app):
        with app.test_client() as client:
            resp = client.get("/route-not-found-404")
            assert resp.status_code == 404
            assert resp.json == {"message": "Resource not found"}

def test_handle_runtime_error(app):
    with app.test_client() as client:
        with patch("app.models.nightline.Nightline.get_nightline") as mock_get_nightline:
            mock_get_nightline.side_effect = RuntimeError("Random unhandled runtime error")
            resp = client.patch("/nightline/test/status", json={"status": "open"})
            
            assert resp.status_code == 500
            assert resp.json == {"message": "An error occurred while processing data"}

def test_handle_generic_error(app):
    with app.test_client() as client:
        with patch("app.models.nightline.Nightline.get_nightline") as mock_get_nightline:
            mock_get_nightline.side_effect = Exception("Random unhandled server error")
            resp = client.patch("/nightline/test/status", json={"status": "open"})
            
            assert resp.status_code == 500
            assert resp.json == {"message": "An unexpected error occurred"}