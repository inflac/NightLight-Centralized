def test_wsgi_import():
    import app.wsgi

    assert app.wsgi.app is not None
